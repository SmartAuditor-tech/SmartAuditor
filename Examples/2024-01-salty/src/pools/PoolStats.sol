// SPDX-License-Identifier: BUSL 1.1
pragma solidity =0.8.22;

import "../../lib/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IExchangeConfig.sol";
import "./interfaces/IPoolsConfig.sol";
import "./interfaces/IPoolStats.sol";
import "./PoolUtils.sol";


// Keeps track of the arbitrage profits generated by pools (for rewards distribution proportional to the profits generated per pool).
abstract contract PoolStats is IPoolStats
	{
	uint64 constant INVALID_POOL_ID = type(uint64).max;

	IExchangeConfig immutable public exchangeConfig;
	IPoolsConfig immutable public poolsConfig;
	IERC20 immutable public _weth;

	// poolID(arbToken2, arbToken3) => arbitrage profits contributed since the last performUpkeep
	mapping(bytes32=>uint256) public _arbitrageProfits;

	// Maps poolID(arbToken2, arbToken3) => the indicies (within the whitelistedPools array) of the pools involved in WETH->arbToken2->arbToken3->WETH
	mapping(bytes32=>ArbitrageIndicies) public _arbitrageIndicies;


    constructor( IExchangeConfig _exchangeConfig, IPoolsConfig _poolsConfig )
    	{
		exchangeConfig = _exchangeConfig;
		poolsConfig = _poolsConfig;

		_weth = exchangeConfig.weth();
    	}


	// Record that arbitrageProfit was generated and the a specific arbitrage path generated it (which is defined by the middle two tokens in WETH->arbToken2->arbToken3->WETH)
	function _updateProfitsFromArbitrage( IERC20 arbToken2, IERC20 arbToken3, uint256 arbitrageProfit ) internal
		{
		// Though three pools contributed to the arbitrage we can record just the middle one as we know the input and output token will be WETH
		bytes32 poolID = PoolUtils._poolID( arbToken2, arbToken3 );

		_arbitrageProfits[poolID] += arbitrageProfit;
		}


	// Called at the end of Upkeep.performUpkeep to reset the arbitrage stats for the pools
	function clearProfitsForPools() external
		{
		require(msg.sender == address(exchangeConfig.upkeep()), "PoolStats.clearProfitsForPools is only callable from the Upkeep contract" );

		bytes32[] memory poolIDs = poolsConfig.whitelistedPools();

		for( uint256 i = 0; i < poolIDs.length; i++ )
			_arbitrageProfits[ poolIDs[i] ] = 0;
		}


	// The index of pool tokenA/tokenB within the whitelistedPools array.
	// Should always find a value as only whitelisted pools are used in the arbitrage path.
	// Returns uint64.max in the event of failed lookup
	function _poolIndex( IERC20 tokenA, IERC20 tokenB, bytes32[] memory poolIDs ) internal pure returns (uint64 index)
		{
		bytes32 poolID = PoolUtils._poolID( tokenA, tokenB );

		for( uint256 i = 0; i < poolIDs.length; i++ )
			{
			if (poolID == poolIDs[i])
				return uint64(i);
			}

		return INVALID_POOL_ID;
		}


	// Traverse the current whitelisted poolIDs and update the indicies of each pool that would contribute to arbitrage for it.
	// Maps poolID(arbToken2, arbToken3) => the indicies (within the whitelistedPools array) of the pools involved in WETH->arbToken2->arbToken3->WETH arbitrage.
	function updateArbitrageIndicies() public
		{
		bytes32[] memory poolIDs = poolsConfig.whitelistedPools();

		for( uint256 i = 0; i < poolIDs.length; i++ )
			{
			bytes32 poolID = poolIDs[i];
			(IERC20 arbToken2, IERC20 arbToken3) = poolsConfig.underlyingTokenPair(poolID);

			// The middle two tokens can never be WETH in a valid arbitrage path as the path is WETH->arbToken2->arbToken3->WETH.
			if ( (arbToken2 != _weth) && (arbToken3 != _weth) )
				{
				uint64 poolIndex1 = _poolIndex( _weth, arbToken2, poolIDs );
				uint64 poolIndex2 = _poolIndex( arbToken2, arbToken3, poolIDs );
				uint64 poolIndex3 = _poolIndex( arbToken3, _weth, poolIDs );

				// Check if the indicies in storage have the correct values - and if not then update them
				ArbitrageIndicies memory indicies = _arbitrageIndicies[poolID];
				if ( ( poolIndex1 != indicies.index1 ) || ( poolIndex2 != indicies.index2 ) || ( poolIndex3 != indicies.index3 ) )
					_arbitrageIndicies[poolID] = ArbitrageIndicies(poolIndex1, poolIndex2, poolIndex3);
				}
			}
		}


	// Examine the arbitrage that has been generated since the last Upkeep.performUpkeep call and credit the pools that have contributed towards it.
	// The calculated sums for each pool will then be used to proportionally distribute SALT rewards to each of the contributing pools.
	function _calculateArbitrageProfits( bytes32[] memory poolIDs, uint256[] memory _calculatedProfits ) internal view
		{
		for( uint256 i = 0; i < poolIDs.length; i++ )
			{
			// references poolID(arbToken2, arbToken3) which defines the arbitage path of WETH->arbToken2->arbToken3->WETH
			bytes32 poolID = poolIDs[i];

			// Split the arbitrage profit between all the pools that contributed to generating the arbitrage for the referenced pool.
			uint256 arbitrageProfit = _arbitrageProfits[poolID] / 3;
			if ( arbitrageProfit > 0 )
				{
				ArbitrageIndicies memory indicies = _arbitrageIndicies[poolID];

				if ( indicies.index1 != INVALID_POOL_ID )
					_calculatedProfits[indicies.index1] += arbitrageProfit;

				if ( indicies.index2 != INVALID_POOL_ID )
					_calculatedProfits[indicies.index2] += arbitrageProfit;

				if ( indicies.index3 != INVALID_POOL_ID )
					_calculatedProfits[indicies.index3] += arbitrageProfit;
				}
			}
		}


	// === VIEWS ===

	// Look at the arbitrage that has been generated since the last performUpkeep and determine how much each of the pools contributed to those generated profits.
	// Returns the profits for all of the current whitelisted pools
	function profitsForWhitelistedPools() external view returns (uint256[] memory _calculatedProfits)
		{
		bytes32[] memory poolIDs = poolsConfig.whitelistedPools();

		_calculatedProfits = new uint256[](poolIDs.length);
		_calculateArbitrageProfits( poolIDs, _calculatedProfits );
		}


	function arbitrageIndicies(bytes32 poolID) external view returns (ArbitrageIndicies memory)
		{
		return _arbitrageIndicies[poolID];
		}
	}