// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";
import "openzeppelin-contracts/contracts/access/Ownable.sol";

/**
 * @title FactoraVaultETH
 * @dev A simplified vault that accepts ETH deposits and allows for trading of idle funds
 */
contract FactoraVaultETH is ERC20, Ownable {
    // Address of the AI agent authorized to trade
    address public agentAddress = 0x709dbF153Ab666000C01c40A044d0ce6824e092c;

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
     * @param _agent Address of the AI agent
     */
    constructor(
        address _agent
    ) ERC20("Factora LP Token", "FACT") Ownable(msg.sender) {}

    /**
     * @dev Get total assets in the vault (ETH balance)
     * @return Total assets in the vault
     */
    function totalAssets() public view returns (uint256) {
        return address(this).balance;
    }

    /**
     * @dev Calculate shares for a given amount of ETH
     * @param assets Amount of ETH to deposit
     * @return Amount of shares to mint
     */
    /**
     * @dev Calculate shares for a given amount of ETH
     * @param assets Amount of ETH to deposit
     * @return Amount of shares to mint
     */
    function _convertToShares(uint256 assets) internal view returns (uint256) {
        uint256 supply = totalSupply();
        uint256 totalVaultAssets = totalAssets();

        if (supply == 0 || totalVaultAssets == 0) {
            return assets; // 1:1 ratio for first deposit
        } else {
            // For subsequent deposits, maintain a consistent ratio between assets and shares
            return (assets * supply) / totalVaultAssets;
        }
    }

    /**
     * @dev Calculate assets for a given amount of shares
     * @param shares Amount of shares to redeem
     * @return Amount of ETH to withdraw
     */
    function _convertToAssets(uint256 shares) internal view returns (uint256) {
        uint256 supply = totalSupply();
        if (supply == 0) {
            return 0;
        } else {
            return (shares * totalAssets()) / supply;
        }
    }

    /**
     * @dev Deposit ETH into the vault
     * @return shares Amount of shares minted
     */
    function deposit() public payable returns (uint256) {
        require(msg.value > 0, "Must deposit some ETH");

        uint256 shares = _convertToShares(msg.value);
        _mint(msg.sender, shares);

        emit Deposited(msg.sender, msg.value, shares);
        return shares;
    }

    /**
     * @dev Allow receiving ETH directly
     */
    receive() external payable {
        deposit();
    }

    /**
     * @dev Withdraw ETH from the vault
     * @param shares Amount of shares to burn
     * @return assets Amount of ETH withdrawn
     */
    function withdraw(uint256 shares) public returns (uint256) {
        require(shares > 0, "Must withdraw some shares");
        require(balanceOf(msg.sender) >= shares, "Not enough shares");

        uint256 assets = _convertToAssets(shares);
        require(assets > 0, "No assets to withdraw");
        require(address(this).balance >= assets, "Not enough ETH in vault");

        _burn(msg.sender, shares);

        (bool success, ) = payable(msg.sender).call{value: assets}("");
        require(success, "ETH transfer failed");

        emit Withdrawn(msg.sender, assets, shares);
        return assets;
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

    /**
     * @dev Allow the owner to withdraw ETH in case of emergency
     * @param amount Amount of ETH to withdraw
     */
    function emergencyWithdraw(uint256 amount) external onlyOwner {
        require(address(this).balance >= amount, "Not enough ETH in vault");
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "ETH transfer failed");
    }
}
