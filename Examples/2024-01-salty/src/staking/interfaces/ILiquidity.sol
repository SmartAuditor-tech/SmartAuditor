// SPDX-License-Identifier: BUSL 1.1
pragma solidity =0.8.22;

import "../../../lib/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import "./IStakingRewards.sol";


interface ILiquidity is IStakingRewards
	{
	function depositLiquidityAndIncreaseShare( IERC20 tokenA, IERC20 tokenB, uint256 maxAmountA, uint256 maxAmountB, uint256 minLiquidityReceived, uint256 deadline, bool useZapping ) external returns (uint256 addedAmountA, uint256 addedAmountB, uint256 addedLiquidity);
	function withdrawLiquidityAndClaim( IERC20 tokenA, IERC20 tokenB, uint256 liquidityToWithdraw, uint256 minReclaimedA, uint256 minReclaimedB, uint256 deadline ) external returns (uint256 reclaimedA, uint256 reclaimedB);
	}
