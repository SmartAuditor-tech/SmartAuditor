// SPDX-License-Identifier: None
pragma solidity ^0.8.19;

import  {TransparentUpgradeableProxy} from "../.cache/OpenZeppelin/v4.9.3/proxy/transparent/TransparentUpgradeableProxy.sol";

contract TransparentUpgradeableProxyReceiveETH is TransparentUpgradeableProxy {
    constructor(address _logic, address admin_, bytes memory _data)
        payable
        TransparentUpgradeableProxy(_logic, admin_, _data)
    {}

    receive() external payable override {}
}
