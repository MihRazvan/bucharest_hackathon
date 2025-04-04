// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/FactoraVault.sol";

contract DeployFactoraVault is Script {
    // Configuration
    address public constant USDC_BASE_SEPOLIA =
        0x036CbD53842c5426634e7929541eC2318f3dCF7e; // USDC on Base Sepolia

    function run() external {
        // Load deployer private key from environment
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address agentAddress = vm.envAddress("AGENT_ADDRESS");

        vm.startBroadcast(deployerPrivateKey);

        // Deploy FactoraVault
        FactoraVault vault = new FactoraVault(
            IERC20(USDC_BASE_SEPOLIA),
            agentAddress
        );

        vm.stopBroadcast();

        // Output the contract address
        console.log("FactoraVault deployed at:", address(vault));
    }
}
