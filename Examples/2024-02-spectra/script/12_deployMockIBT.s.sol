// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.20;

import "../lib/forge-std/src/Script.sol";
import "../lib/forge-std/src/Vm.sol";
import "../lib/forge-std/src/console.sol";
import "../src/mocks/MockIBTBeta.sol";
import "../lib/openzeppelin-contracts/contracts/interfaces/IERC20Metadata.sol";

contract MockIBTBetaScript is Script {
    function run() public {
        vm.startBroadcast();
        string memory deploymentNetwork = vm.envString("DEPLOYMENT_NETWORK");
        if (bytes(deploymentNetwork).length == 0) {
            revert("DEPLOYMENT_NETWORK is not set in .env file");
        }

        if (bytes(vm.envString(string.concat("ASSET_ADDR_", deploymentNetwork))).length == 0) {
            revert("ASSET_ADDR_ is not set in .env file");
        }
        address asset = vm.envAddress(string.concat("ASSET_ADDR_", deploymentNetwork));

        MockIBTBeta ibt = new MockIBTBeta();
        ibt.initialize("MOCK IBT", "MCKIBT", IERC20Metadata(asset));
        console.log("IBT deployed at", address(ibt));
        vm.stopBroadcast();
    }
}
