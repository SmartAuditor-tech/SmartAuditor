// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0;

import "../utils/BaseScript.sol";
import  {LockingMultiRewards} from "../src/staking/LockingMultiRewards.sol";

contract LockingMultiRewardsScript is BaseScript {
    function deploy() public returns (LockingMultiRewards staking) {
        address safe = toolkit.getAddress(block.chainid, "safe.ops");

        vm.startBroadcast();
        staking = deployWithParameters(toolkit.getAddress(block.chainid, "mim"), 30_000, 7 days, 13 weeks, tx.origin);

        staking.addReward(toolkit.getAddress(block.chainid, "arb"));
        staking.setMinLockAmount(100 ether);

        if (!testing()) {
            staking.transferOwnership(safe);
        }
        vm.stopBroadcast();
    }

    function deployWithParameters(
        address stakingToken,
        uint256 boost,
        uint256 rewardDuration,
        uint256 lockDuration,
        address origin
    ) public returns (LockingMultiRewards staking) {
        bytes memory params = abi.encode(stakingToken, boost, rewardDuration, lockDuration, origin);
        staking = LockingMultiRewards(deploy("LockingMultiRewards", "LockingMultiRewards.sol:LockingMultiRewards", params));
    }
}
