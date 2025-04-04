// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import "openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol";
import "openzeppelin-contracts/contracts/access/Ownable.sol";
import "openzeppelin-contracts/contracts/token/ERC20/extensions/ERC4626.sol";

/**
 * @title FactoraVault
 * @dev A simplified vault that accepts deposits and allows for trading of idle funds
 */
contract FactoraVault is ERC4626, Ownable {
    using SafeERC20 for IERC20;

    // Address of the AI agent authorized to trade
    address public agentAddress;

    // Trading parameters
    uint256 public maxTradingPercentage = 5000; // 50%

    // Trading stats
    uint256 public totalTraded;
    uint256 public totalProfitGenerated;

    // Events
    event Deposited(address indexed user, uint256 amount, uint256 shares);
    event Withdrawn(address indexed user, uint256 amount, uint256 shares);
    event IdleFundsTraded(uint256 amount, string strategy);
    event TradingProfitReported(uint256 profit);
    event MaxTradingPercentageUpdated(uint256 newPercentage);
    event AgentAddressUpdated(address newAgent);

    /**
     * @dev Constructor
     * @param _asset Address of the stablecoin used for the vault
     * @param _agent Address of the AI agent
     */
    constructor(
        IERC20 _asset,
        address _agent
    ) ERC4626(_asset) ERC20("Factora LP Token", "FACT") Ownable(msg.sender) {
        agentAddress = _agent;
    }

    /**
     * @dev Override of totalAssets to account for potential profits from trading
     * @return Total assets in the vault
     */
    function totalAssets() public view override returns (uint256) {
        return IERC20(asset()).balanceOf(address(this));
    }

    /**
     * @dev Deposit assets into the vault
     * @param assets Amount of assets to deposit
     * @param receiver Address receiving the LP tokens
     * @return shares Amount of shares minted
     */
    function deposit(
        uint256 assets,
        address receiver
    ) public override returns (uint256) {
        uint256 shares = super.deposit(assets, receiver);
        emit Deposited(receiver, assets, shares);
        return shares;
    }

    /**
     * @dev Withdraw assets from the vault
     * @param assets Amount of assets to withdraw
     * @param receiver Address receiving the assets
     * @param owner Owner of the shares
     * @return shares Amount of shares burned
     */
    function withdraw(
        uint256 assets,
        address receiver,
        address owner
    ) public override returns (uint256) {
        uint256 shares = super.withdraw(assets, receiver, owner);
        emit Withdrawn(receiver, assets, shares);
        return shares;
    }

    /**
     * @dev Get vault stats
     * @return totalFunds Total funds in the vault
     * @return availableForTrading Amount available for trading
     */
    function getVaultStats()
        external
        view
        returns (uint256 totalFunds, uint256 availableForTrading)
    {
        totalFunds = totalAssets();
        availableForTrading = (totalFunds * maxTradingPercentage) / 10000;

        return (totalFunds, availableForTrading);
    }

    /**
     * @dev Trade idle funds according to a specified strategy
     * @param strategyId Identifier of the trading strategy
     * @param amountToTrade Amount of assets to trade
     * @return success Whether the trade was initiated successfully
     */
    function tradeIdleFunds(
        string memory strategyId,
        uint256 amountToTrade
    ) external returns (bool) {
        require(
            msg.sender == agentAddress || msg.sender == owner(),
            "Only agent or owner can trade"
        );

        uint256 maxTradeAmount = (totalAssets() * maxTradingPercentage) / 10000;
        require(amountToTrade <= maxTradeAmount, "Trade amount exceeds limit");

        // In a real implementation, this would interact with DEXes via AgentKit
        // For now, we'll just emit an event
        totalTraded += amountToTrade;

        emit IdleFundsTraded(amountToTrade, strategyId);

        return true;
    }

    /**
     * @dev Report profits from a trading strategy
     * @param profit Amount of profit generated
     * @return success Whether the profit was successfully reported
     */
    function reportTradingProfit(uint256 profit) external returns (bool) {
        require(
            msg.sender == agentAddress || msg.sender == owner(),
            "Only agent or owner can report"
        );

        totalProfitGenerated += profit;

        emit TradingProfitReported(profit);

        return true;
    }

    /**
     * @dev Update the maximum trading percentage
     * @param newPercentage New maximum trading percentage (in basis points)
     */
    function updateMaxTradingPercentage(
        uint256 newPercentage
    ) external onlyOwner {
        require(newPercentage <= 8000, "Percentage cannot exceed 80%");
        maxTradingPercentage = newPercentage;
        emit MaxTradingPercentageUpdated(newPercentage);
    }

    /**
     * @dev Update the agent address
     * @param newAgent New agent address
     */
    function updateAgentAddress(address newAgent) external onlyOwner {
        require(newAgent != address(0), "Invalid agent address");
        agentAddress = newAgent;
        emit AgentAddressUpdated(newAgent);
    }
}
