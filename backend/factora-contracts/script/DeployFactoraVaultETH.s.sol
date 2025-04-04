// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/FactoraVaultETH.sol";

contract DeployFactoraVaultETH is Script {
    function run() external {
        // Load deployer private key from environment
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address agentAddress = vm.envAddress("AGENT_ADDRESS");

        vm.startBroadcast(deployerPrivateKey);

        // Deploy FactoraVaultETH
        FactoraVaultETH vault = new FactoraVaultETH(agentAddress);

        vm.stopBroadcast();

        // Output the contract address
        console.log("FactoraVaultETH deployed at:", address(vault));
    }
}
