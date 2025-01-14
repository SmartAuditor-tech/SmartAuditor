// SPDX-License-Identifier: MIT
pragma solidity =0.8.17;

import "../../lib/forge-std/src/Script.sol";
import {DeployBase} from "./DeployBase.s.sol";
import {Parameters} from "../../src/params/Parameters.sol";

contract DeployMainnet is Script, Parameters {
  function run() public {
    new DeployBase().deploy(
      MAINNET_OWNER,
      MAINNET_DNFT,
      MAINNET_WETH,
      MAINNET_WETH_ORACLE,
      MAINNET_FEE, 
      MAINNET_FEE_RECIPIENT
    );
  }
}
