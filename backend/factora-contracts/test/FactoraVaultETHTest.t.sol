// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/FactoraVaultETH.sol";

contract FactoraVaultETHTest is Test {
    FactoraVaultETH public vault;

    address public owner;
    address public agent;
    address public depositor1;
    address public depositor2;

    uint256 public constant INITIAL_BALANCE = 100 ether;
    uint256 public constant DEPOSIT_AMOUNT = 10 ether;

    // Add receive function to accept ETH transfers
    receive() external payable {}

    function setUp() public {
        // Set up accounts
        owner = address(this);
        agent = makeAddr("agent");
        depositor1 = makeAddr("depositor1");
        depositor2 = makeAddr("depositor2");

        // Fund accounts
        vm.deal(depositor1, INITIAL_BALANCE);
        vm.deal(depositor2, INITIAL_BALANCE);

        // Deploy vault
        vault = new FactoraVaultETH(agent);
    }

    function testDeposit() public {
        uint256 initialDepositorBalance = address(depositor1).balance;
        uint256 initialVaultBalance = address(vault).balance;

        // Perform deposit
        vm.startPrank(depositor1);
        uint256 shares = vault.deposit{value: DEPOSIT_AMOUNT}();
        vm.stopPrank();

        // Check balances
        assertEq(
            address(depositor1).balance,
            initialDepositorBalance - DEPOSIT_AMOUNT
        );
        assertEq(address(vault).balance, initialVaultBalance + DEPOSIT_AMOUNT);

        // Check shares
        assertEq(vault.balanceOf(depositor1), shares);
        assertEq(shares, DEPOSIT_AMOUNT); // 1:1 ratio on first deposit
    }

    function testDirectDeposit() public {
        uint256 initialDepositorBalance = address(depositor1).balance;
        uint256 initialVaultBalance = address(vault).balance;

        // Perform direct deposit (send ETH)
        vm.startPrank(depositor1);
        (bool success, ) = address(vault).call{value: DEPOSIT_AMOUNT}("");
        require(success, "Transfer failed");
        vm.stopPrank();

        // Check balances
        assertEq(
            address(depositor1).balance,
            initialDepositorBalance - DEPOSIT_AMOUNT
        );
        assertEq(address(vault).balance, initialVaultBalance + DEPOSIT_AMOUNT);

        // Check shares
        assertEq(vault.balanceOf(depositor1), DEPOSIT_AMOUNT); // 1:1 ratio on first deposit
    }

    function testMultipleDeposits() public {
        // First depositor
        vm.startPrank(depositor1);
        uint256 shares1 = vault.deposit{value: DEPOSIT_AMOUNT}();
        vm.stopPrank();

        // At this point, the relationship is 1:1 (10 ETH = 10 shares)
        assertEq(shares1, DEPOSIT_AMOUNT);

        // Second depositor (should also get the same amount of shares for same ETH)
        vm.startPrank(depositor2);
        uint256 shares2 = vault.deposit{value: DEPOSIT_AMOUNT}();
        vm.stopPrank();

        // Second deposit should also receive the same amount of shares
        assertEq(shares2, DEPOSIT_AMOUNT);

        // Check total assets and total shares
        assertEq(vault.totalAssets(), DEPOSIT_AMOUNT * 2);
        assertEq(vault.totalSupply(), DEPOSIT_AMOUNT * 2);
    }

    function testWithdraw() public {
        // First deposit
        vm.startPrank(depositor1);
        vault.deposit{value: DEPOSIT_AMOUNT}();
        vm.stopPrank();

        uint256 initialDepositorBalance = address(depositor1).balance;
        uint256 initialVaultBalance = address(vault).balance;

        // Perform withdrawal
        vm.startPrank(depositor1);
        uint256 assets = vault.withdraw(DEPOSIT_AMOUNT / 2);
        vm.stopPrank();

        // Check balances
        assertEq(
            address(depositor1).balance,
            initialDepositorBalance + DEPOSIT_AMOUNT / 2
        );
        assertEq(
            address(vault).balance,
            initialVaultBalance - DEPOSIT_AMOUNT / 2
        );

        // Check shares
        assertEq(vault.balanceOf(depositor1), DEPOSIT_AMOUNT / 2);
        assertEq(assets, DEPOSIT_AMOUNT / 2);
    }

    function testTradingPermissions() public {
        // Deposit funds
        vm.startPrank(depositor1);
        vault.deposit{value: DEPOSIT_AMOUNT}();
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
        vault.deposit{value: DEPOSIT_AMOUNT}();
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
        vault.deposit{value: DEPOSIT_AMOUNT}();
        vm.stopPrank();

        // Agent reports profit
        uint256 profit = 1 ether;
        vm.startPrank(agent);
        bool success = vault.reportTradingProfit(profit);
        assertEq(success, true);
        vm.stopPrank();

        // Check profit tracking
        assertEq(vault.totalProfitGenerated(), profit);

        // Add actual profit by sending ETH to the vault
        vm.deal(address(this), profit);
        (bool sent, ) = payable(address(vault)).call{value: profit}("");
        require(sent, "Failed to send ETH");

        // Check total assets increased
        assertEq(vault.totalAssets(), DEPOSIT_AMOUNT + profit);
    }

    function testEmergencyWithdraw() public {
        // Deposit funds
        vm.startPrank(depositor1);
        vault.deposit{value: DEPOSIT_AMOUNT}();
        vm.stopPrank();

        uint256 initialOwnerBalance = address(this).balance;

        // Perform emergency withdrawal
        uint256 withdrawAmount = DEPOSIT_AMOUNT / 2;
        vault.emergencyWithdraw(withdrawAmount);

        // Check balances
        assertEq(address(this).balance, initialOwnerBalance + withdrawAmount);
        assertEq(address(vault).balance, DEPOSIT_AMOUNT - withdrawAmount);
    }
}
