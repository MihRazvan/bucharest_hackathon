// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/FactoraVault.sol";
import "openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";

// Mock ERC20 token for testing
contract MockToken is ERC20 {
    constructor() ERC20("USD Coin", "USDC") {
        _mint(msg.sender, 1_000_000 * 10 ** 18);
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

contract FactoraVaultTest is Test {
    FactoraVault public vault;
    MockToken public token;

    address public owner;
    address public agent;
    address public depositor1;
    address public depositor2;

    uint256 public constant INITIAL_SUPPLY = 1_000_000 * 10 ** 18;
    uint256 public constant DEPOSIT_AMOUNT = 100_000 * 10 ** 18;

    function setUp() public {
        // Set up accounts
        owner = address(this);
        agent = makeAddr("agent");
        depositor1 = makeAddr("depositor1");
        depositor2 = makeAddr("depositor2");

        // Deploy mock token
        token = new MockToken();

        // Deploy vault
        vault = new FactoraVault(IERC20(address(token)), agent);

        // Transfer tokens to depositors
        token.transfer(depositor1, DEPOSIT_AMOUNT);
        token.transfer(depositor2, DEPOSIT_AMOUNT);

        // Approve vault to spend tokens
        vm.startPrank(depositor1);
        token.approve(address(vault), DEPOSIT_AMOUNT);
        vm.stopPrank();

        vm.startPrank(depositor2);
        token.approve(address(vault), DEPOSIT_AMOUNT);
        vm.stopPrank();
    }

    function testDeposit() public {
        uint256 initialDepositorBalance = token.balanceOf(depositor1);
        uint256 initialVaultBalance = token.balanceOf(address(vault));

        // Perform deposit
        vm.startPrank(depositor1);
        uint256 shares = vault.deposit(DEPOSIT_AMOUNT / 2, depositor1);
        vm.stopPrank();

        // Check balances
        assertEq(
            token.balanceOf(depositor1),
            initialDepositorBalance - DEPOSIT_AMOUNT / 2
        );
        assertEq(
            token.balanceOf(address(vault)),
            initialVaultBalance + DEPOSIT_AMOUNT / 2
        );

        // Check shares
        assertEq(vault.balanceOf(depositor1), shares);
        assertEq(shares, DEPOSIT_AMOUNT / 2); // 1:1 ratio on first deposit
    }

    function testMultipleDeposits() public {
        // First depositor
        vm.startPrank(depositor1);
        uint256 shares1 = vault.deposit(DEPOSIT_AMOUNT / 2, depositor1);
        vm.stopPrank();

        // Second depositor
        vm.startPrank(depositor2);
        uint256 shares2 = vault.deposit(DEPOSIT_AMOUNT / 2, depositor2);
        vm.stopPrank();

        // Check total assets
        assertEq(vault.totalAssets(), DEPOSIT_AMOUNT);

        // Check that shares are the same (1:1 ratio)
        assertEq(shares1, shares2);
    }

    function testWithdraw() public {
        // First deposit
        vm.startPrank(depositor1);
        uint256 shares = vault.deposit(DEPOSIT_AMOUNT / 2, depositor1);
        vm.stopPrank();

        uint256 initialDepositorBalance = token.balanceOf(depositor1);
        uint256 initialVaultBalance = token.balanceOf(address(vault));

        // Perform withdrawal
        vm.startPrank(depositor1);
        uint256 assets = vault.withdraw(
            DEPOSIT_AMOUNT / 4,
            depositor1,
            depositor1
        );
        vm.stopPrank();

        // Check balances
        assertEq(
            token.balanceOf(depositor1),
            initialDepositorBalance + DEPOSIT_AMOUNT / 4
        );
        assertEq(
            token.balanceOf(address(vault)),
            initialVaultBalance - DEPOSIT_AMOUNT / 4
        );

        // Check shares
        assertEq(vault.balanceOf(depositor1), shares - DEPOSIT_AMOUNT / 4);
        assertEq(assets, DEPOSIT_AMOUNT / 4);
    }

    function testTradingPermissions() public {
        // Deposit funds
        vm.startPrank(depositor1);
        vault.deposit(DEPOSIT_AMOUNT, depositor1);
        vm.stopPrank();

        // Random address cannot trade
        address randomUser = makeAddr("random");
        vm.startPrank(randomUser);
        vm.expectRevert("Only agent or owner can trade");
        vault.tradeIdleFunds("strategy1", DEPOSIT_AMOUNT / 10);
        vm.stopPrank();

        // Agent can trade
        vm.startPrank(agent);
        bool success = vault.tradeIdleFunds("strategy1", DEPOSIT_AMOUNT / 10);
        assertEq(success, true);
        vm.stopPrank();

        // Owner can trade
        vm.startPrank(owner);
        success = vault.tradeIdleFunds("strategy2", DEPOSIT_AMOUNT / 10);
        assertEq(success, true);
        vm.stopPrank();
    }

    function testTradingLimits() public {
        // Deposit funds
        vm.startPrank(depositor1);
        vault.deposit(DEPOSIT_AMOUNT, depositor1);
        vm.stopPrank();

        // Default maxTradingPercentage is 50%
        (uint256 totalFunds, uint256 availableForTrading) = vault
            .getVaultStats();
        assertEq(totalFunds, DEPOSIT_AMOUNT);
        assertEq(availableForTrading, DEPOSIT_AMOUNT / 2);

        // Trading within limits should succeed
        vm.startPrank(agent);
        bool success = vault.tradeIdleFunds("strategy1", DEPOSIT_AMOUNT / 2);
        assertEq(success, true);
        vm.stopPrank();

        // Trading beyond limits should fail
        vm.startPrank(agent);
        vm.expectRevert("Trade amount exceeds limit");
        vault.tradeIdleFunds("strategy2", (DEPOSIT_AMOUNT * 3) / 4);
        vm.stopPrank();

        // Update trading limits
        vm.startPrank(owner);
        vault.updateMaxTradingPercentage(8000); // 80%
        vm.stopPrank();

        // Check new limits
        (, availableForTrading) = vault.getVaultStats();
        assertEq(availableForTrading, (DEPOSIT_AMOUNT * 8) / 10);

        // Trading with new limits should succeed
        vm.startPrank(agent);
        success = vault.tradeIdleFunds("strategy3", (DEPOSIT_AMOUNT * 7) / 10);
        assertEq(success, true);
        vm.stopPrank();
    }

    function testReportTradingProfit() public {
        // Deposit funds
        vm.startPrank(depositor1);
        vault.deposit(DEPOSIT_AMOUNT, depositor1);
        vm.stopPrank();

        // Agent reports profit
        uint256 profit = 1000 * 10 ** 18;
        vm.startPrank(agent);
        bool success = vault.reportTradingProfit(profit);
        assertEq(success, true);
        vm.stopPrank();

        // Check profit tracking
        assertEq(vault.totalProfitGenerated(), profit);

        // Add actual profit by minting tokens to the vault
        token.mint(address(vault), profit);

        // Check total assets increased
        assertEq(vault.totalAssets(), DEPOSIT_AMOUNT + profit);
    }
}
