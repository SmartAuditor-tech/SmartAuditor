# Report

## Gas Optimizations

| |Issue|Instances|
|-|:-|:-:|
| [GAS-1](#GAS-1) | `a = a + b` is more gas effective than `a += b` for state variables (excluding arrays and mappings) | 12 |
| [GAS-2](#GAS-2) | Use assembly to check for `address(0)` | 8 |
| [GAS-3](#GAS-3) | Using bools for storage incurs overhead | 1 |
| [GAS-4](#GAS-4) | State variables should be cached in stack variables rather than re-reading them from storage | 4 |
| [GAS-5](#GAS-5) | For Operations that will not overflow, you could use unchecked | 113 |
| [GAS-6](#GAS-6) | Use Custom Errors instead of Revert Strings to save Gas | 18 |
| [GAS-7](#GAS-7) | State variables only set in the constructor should be declared `immutable` | 5 |
| [GAS-8](#GAS-8) | Functions guaranteed to revert when called by normal users can be marked `payable` | 3 |
| [GAS-9](#GAS-9) | `++i` costs less gas compared to `i++` or `i += 1` (same for `--i` vs `i--` or `i -= 1`) | 3 |
| [GAS-10](#GAS-10) | Using `private` rather than `public` for constants, saves gas | 3 |
| [GAS-11](#GAS-11) | Splitting require() statements that use && saves gas | 6 |
| [GAS-12](#GAS-12) | Use != 0 instead of > 0 for unsigned integer comparison | 24 |
| [GAS-13](#GAS-13) | `internal` functions not called by the contract should be removed | 2 |
| [GAS-14](#GAS-14) | WETH address definition can be use directly | 2 |

### <a name="GAS-1"></a>[GAS-1] `a = a + b` is more gas effective than `a += b` for state variables (excluding arrays and mappings)

This saves **16 gas per instance.**

*Instances (12)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

227:         position.tokensOwed0 += uint128(

232:         position.tokensOwed1 += uint128(

240:         position.liquidity += liquidity;

272:         position.tokensOwed0 += uint128(amount0)

278:         position.tokensOwed1 += uint128(amount1)

321:             tokensOwed0 += uint128(

326:             tokensOwed1 += uint128(

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

647:                 state.amountSpecifiedRemaining += step.amountOut.toInt256();

655:                 state.protocolFee += uint128(delta);

660:                 state.feeGrowthGlobalX128 += FullMath.mulDiv(step.feeAmount, FixedPoint128.Q128, state.liquidity);

731:             if (state.protocolFee > 0) protocolFees.token0 += state.protocolFee;

734:             if (state.protocolFee > 0) protocolFees.token1 += state.protocolFee;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="GAS-2"></a>[GAS-2] Use assembly to check for `address(0)`

*Saves 6 gas per instance*

*Instances (8)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

305:         address recipient = params.recipient == address(0) ? address(this) : params.recipient;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

597:         if (address(gauge) != address(0)) {

681:                     if (gauge != address(0)) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

51:         require(token0 != address(0));

54:         require(getPool[token0][token1][fee] == address(0));

66:         require(_owner != address(0));

72:         require(msg.sender == owner && deployer == address(0), "INVALID");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

```solidity
File: contracts/base/PoolInitializer.sol

23:         if (pool == address(0)) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/base/PoolInitializer.sol)

### <a name="GAS-3"></a>[GAS-3] Using bools for storage incurs overhead

Use uint256(1) and uint256(2) for true/false to avoid a Gwarmaccess (100 gas), and to avoid Gsset (20000 gas) when changing from ‘false’ to ‘true’, after having been ‘true’ in the past. See [source](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/58f635312aa21f947cae5f8578638a85aa2519f5/contracts/security/ReentrancyGuard.sol#L23-L27).

*Instances (1)*:

```solidity
File: contracts/ThrusterPoolFactory.sol

27:     mapping(address => bool) public poolExists;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="GAS-4"></a>[GAS-4] State variables should be cached in stack variables rather than re-reading them from storage

The instances below point to the second+ access of a state variable within a function. Caching of a state variable replaces each Gwarmaccess (100 gas) with a much cheaper stack read. Other less obvious fixes/optimizations include having local memory caches of state variable structs, or having local caches of state variable contracts/addresses.

*Saves 100 gas per instance*

*Instances (4)*:

```solidity
File: contracts/ThrusterPool.sol

403:                 maxLiquidityPerTick

410:                 tickBitmap.flipTick(tickUpper, tickSpacing);

598:             IThrusterGauge(gauge).checkpoint(cache.blockTimestamp);

682:                         IThrusterGauge(gauge).cross(step.tickNext, zeroForOne);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="GAS-5"></a>[GAS-5] For Operations that will not overflow, you could use unchecked

*Instances (113)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

5: import "interfaces/INonfungiblePositionManager.sol";

6: import "interfaces/INonfungibleTokenPositionDescriptor.sol";

7: import "interfaces/IThrusterPool.sol";

9: import "contracts/ThrusterGas.sol";

10: import "contracts/base/ERC721Permit.sol";

11: import "contracts/base/LiquidityManagement.sol";

12: import "contracts/base/Multicall.sol";

13: import "contracts/base/PeripheryImmutableState.sol";

14: import "contracts/base/PeripheryValidation.sol";

15: import "contracts/base/PoolInitializer.sol";

16: import "contracts/base/SelfPermit.sol";

17: import "contracts/libraries/FixedPoint128.sol";

18: import "contracts/libraries/FullMath.sol";

19: import "contracts/libraries/PoolAddress.sol";

20: import "contracts/libraries/PositionKey.sol";

74:         ERC721Permit("Thruster Positions NFT", "THRUST-POS", "1")

124:             _poolIds[pool] = (poolId = _nextPoolId++);

153:         _mint(params.recipient, (tokenId = _nextId++));

227:         position.tokensOwed0 += uint128(

229:                 feeGrowthInside0LastX128 - position.feeGrowthInside0LastX128, position.liquidity, FixedPoint128.Q128

232:         position.tokensOwed1 += uint128(

234:                 feeGrowthInside1LastX128 - position.feeGrowthInside1LastX128, position.liquidity, FixedPoint128.Q128

240:         position.liquidity += liquidity;

272:         position.tokensOwed0 += uint128(amount0)

273:             + uint128(

275:                     feeGrowthInside0LastX128 - position.feeGrowthInside0LastX128, positionLiquidity, FixedPoint128.Q128

278:         position.tokensOwed1 += uint128(amount1)

279:             + uint128(

281:                     feeGrowthInside1LastX128 - position.feeGrowthInside1LastX128, positionLiquidity, FixedPoint128.Q128

288:         position.liquidity = positionLiquidity - params.liquidity;

321:             tokensOwed0 += uint128(

323:                     feeGrowthInside0LastX128 - position.feeGrowthInside0LastX128, position.liquidity, FixedPoint128.Q128

326:             tokensOwed1 += uint128(

328:                     feeGrowthInside1LastX128 - position.feeGrowthInside1LastX128, position.liquidity, FixedPoint128.Q128

348:         (position.tokensOwed0, position.tokensOwed1) = (tokensOwed0 - amount0Collect, tokensOwed1 - amount1Collect);

370:         return uint256(_positions[tokenId].nonce++);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

4: import "interfaces/IERC20Minimal.sol";

5: import "interfaces/IThrusterPoolFactory.sol";

6: import "interfaces/IThrusterGauge.sol";

7: import "interfaces/IThrusterPool.sol";

8: import "interfaces/IThrusterPoolDeployer.sol";

9: import "interfaces/callback/IThrusterMintCallback.sol";

10: import "interfaces/callback/IThrusterSwapCallback.sol";

11: import "interfaces/callback/IThrusterFlashCallback.sol";

13: import "interfaces/IBlast.sol";

14: import "interfaces/IERC20Rebasing.sol";

16: import "contracts/NoDelegateCall.sol";

17: import "contracts/libraries/FixedPoint128.sol";

18: import "contracts/libraries/FullMath.sol";

19: import "contracts/libraries/LiquidityMath.sol";

20: import "contracts/libraries/LowGasSafeMath.sol";

21: import "contracts/libraries/Oracle.sol";

22: import "contracts/libraries/Position.sol";

23: import "contracts/libraries/SafeCast.sol";

24: import "contracts/libraries/SqrtPriceMath.sol";

25: import "contracts/libraries/SwapMath.sol";

26: import "contracts/libraries/Tick.sol";

27: import "contracts/libraries/TickMath.sol";

28: import "contracts/libraries/TickBitmap.sol";

29: import "contracts/libraries/TransferHelper.sol";

209:                 tickCumulativeLower - tickCumulativeUpper,

210:                 secondsPerLiquidityOutsideLowerX128 - secondsPerLiquidityOutsideUpperX128,

211:                 secondsOutsideLower - secondsOutsideUpper

219:                 tickCumulative - tickCumulativeLower - tickCumulativeUpper,

220:                 secondsPerLiquidityCumulativeX128 - secondsPerLiquidityOutsideLowerX128

221:                     - secondsPerLiquidityOutsideUpperX128,

222:                 time - secondsOutsideLower - secondsOutsideUpper

226:                 tickCumulativeUpper - tickCumulativeLower,

227:                 secondsPerLiquidityOutsideUpperX128 - secondsPerLiquidityOutsideLowerX128,

228:                 secondsOutsideUpper - secondsOutsideLower

258:         uint16 observationCardinalityNextOld = slot0.observationCardinalityNext; // for the event

311:         Slot0 memory _slot0 = slot0; // SLOAD for gas optimization

326:                 uint128 liquidityBefore = liquidity; // SLOAD for gas optimization

369:         uint256 _feeGrowthGlobal0X128 = feeGrowthGlobal0X128; // SLOAD for gas optimization

370:         uint256 _feeGrowthGlobal1X128 = feeGrowthGlobal1X128; // SLOAD for gas optimization

477:             position.tokensOwed0 -= amount0;

481:             position.tokensOwed1 -= amount1;

501:                 liquidityDelta: -int256(amount).toInt128()

505:         amount0 = uint256(-amount0Int);

506:         amount1 = uint256(-amount1Int);

510:                 (position.tokensOwed0 + uint128(amount0), position.tokensOwed1 + uint128(amount1));

644:                 state.amountSpecifiedRemaining -= (step.amountIn + step.feeAmount).toInt256();

647:                 state.amountSpecifiedRemaining += step.amountOut.toInt256();

648:                 state.amountCalculated = state.amountCalculated.add((step.amountIn + step.feeAmount).toInt256());

653:                 uint256 delta = step.feeAmount / cache.feeProtocol;

654:                 step.feeAmount -= delta;

655:                 state.protocolFee += uint128(delta);

660:                 state.feeGrowthGlobalX128 += FullMath.mulDiv(step.feeAmount, FixedPoint128.Q128, state.liquidity);

695:                     if (zeroForOne) liquidityNet = -liquidityNet;

700:                 state.tick = zeroForOne ? step.tickNext - 1 : step.tickNext;

731:             if (state.protocolFee > 0) protocolFees.token0 += state.protocolFee;

734:             if (state.protocolFee > 0) protocolFees.token1 += state.protocolFee;

738:             ? (amountSpecified - state.amountSpecifiedRemaining, state.amountCalculated)

739:             : (state.amountCalculated, amountSpecified - state.amountSpecifiedRemaining);

743:             if (amount1 < 0) TransferHelper.safeTransfer(token1, recipient, uint256(-amount1));

749:             if (amount0 < 0) TransferHelper.safeTransfer(token0, recipient, uint256(-amount0));

769:         slot0.feeProtocol = feeProtocol0 + (feeProtocol1 << 4);

784:             if (amount0 == protocolFees.token0) amount0--; // ensure that the slot is not cleared, for gas savings

785:             protocolFees.token0 -= amount0;

789:             if (amount1 == protocolFees.token1) amount1--; // ensure that the slot is not cleared, for gas savings

790:             protocolFees.token1 -= amount1;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolDeployer.sol

4: import "interfaces/IThrusterPoolDeployer.sol";

6: import "contracts/ThrusterPool.sol";

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

4: import "interfaces/IThrusterPoolFactory.sol";

5: import "interfaces/IThrusterPoolDeployer.sol";

7: import "contracts/NoDelegateCall.sol";

8: import "contracts/ThrusterGas.sol";

9: import "contracts/ThrusterPool.sol";

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

```solidity
File: contracts/base/PoolInitializer.sol

4: import "interfaces/IPoolInitializer.sol";

5: import "interfaces/IThrusterPoolFactory.sol";

6: import "interfaces/IThrusterPoolDeployer.sol";

7: import "interfaces/IThrusterPool.sol";

9: import "./PeripheryImmutableState.sol";

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/base/PoolInitializer.sol)

### <a name="GAS-6"></a>[GAS-6] Use Custom Errors instead of Revert Strings to save Gas

Custom errors are available from solidity version 0.8.4. Custom errors save [**~50 gas**](https://gist.github.com/IllIllI000/ad1bd0d29a0101b25e57c293b4b0c746) each time they're hit by [avoiding having to allocate and store the revert string](https://blog.soliditylang.org/2021/04/21/custom-errors/#errors-in-depth). Not defining the strings also save deployment gas

Additionally, custom errors can be used inside and outside of contracts (including interfaces and libraries).

Source: <https://blog.soliditylang.org/2021/04/21/custom-errors/>:

> Starting from [Solidity v0.8.4](https://github.com/ethereum/solidity/releases/tag/v0.8.4), there is a convenient and gas-efficient way to explain to users why an operation failed through the use of custom errors. Until now, you could already use strings to give more information about failures (e.g., `revert("Insufficient funds.");`), but they are rather expensive, especially when it comes to deploy cost, and it is difficult to use dynamic information in them.

Consider replacing **all revert strings** with custom errors in the solution, and particularly those that have multiple occurrences:

*Instances (18)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

102:         require(position.poolId != 0, "Invalid token ID");

182:         require(_isApprovedOrOwner(msg.sender, tokenId), "Not approved");

266:         require(amount0 >= params.amount0Min && amount1 >= params.amount1Min, "Price slippage check");

364:         require(position.liquidity == 0 && position.tokensOwed0 == 0 && position.tokensOwed1 == 0, "Not cleared");

375:         require(_exists(tokenId), "ERC721: approved query for nonexistent token");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

115:         require(slot0.unlocked, "LOK");

141:         require(tickLower < tickUpper, "TLU");

142:         require(tickLower >= TickMath.MIN_TICK, "TLM");

143:         require(tickUpper <= TickMath.MAX_TICK, "TUM");

270:         require(slot0.sqrtPriceX96 == 0, "AI");

456:         if (amount0 > 0) require(balance0Before.add(amount0) <= balance0(), "M0");

457:         if (amount1 > 0) require(balance1Before.add(amount1) <= balance1(), "M1");

574:         require(amountSpecified != 0, "AS");

578:         require(slot0Start.unlocked, "LOK");

747:             require(balance0Before.add(uint256(amount0)) <= balance0(), "IIA");

753:             require(balance1Before.add(uint256(amount1)) <= balance1(), "IIA");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

72:         require(msg.sender == owner && deployer == address(0), "INVALID");

104:         require(poolExists[msg.sender], "INVALID_POOL");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="GAS-7"></a>[GAS-7] State variables only set in the constructor should be declared `immutable`

Variables only set in the constructor and never edited afterwards should be marked as immutable, as it would avoid the expensive storage-writing operation in the constructor (around **20 000 gas** per variable) and replace the expensive storage-reading operations (around **2100 gas** per reading) to a less expensive value reading (**3 gas**)

*Instances (5)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

78:         _tokenDescriptor = _tokenDescriptor_;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

134:         tickSpacing = _tickSpacing;

136:         maxLiquidityPerTick = Tick.tickSpacingToMaxLiquidityPerTick(_tickSpacing);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolDeployer.sol

30:         factory = _factory;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

32:         pointsAdmin = _pointsAdmin;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="GAS-8"></a>[GAS-8] Functions guaranteed to revert when called by normal users can be marked `payable`

If a function modifier such as `onlyOwner` is used, the function will revert if a normal user tries to pay the function. Marking the function as `payable` will lower the gas cost for legitimate callers because the compiler will not include checks for whether a payment was provided.

*Instances (3)*:

```solidity
File: contracts/ThrusterPool.sol

764:     function setFeeProtocol(uint8 feeProtocol0, uint8 feeProtocol1) external override lock onlyFactoryOwner {

798:     function setGauge(address _gauge) external override lock onlyFactoryOwner {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolDeployer.sol

45:     function claimGas(address _recipient) external override onlyFactory returns (uint256 amount) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

### <a name="GAS-9"></a>[GAS-9] `++i` costs less gas compared to `i++` or `i += 1` (same for `--i` vs `i--` or `i -= 1`)

Pre-increments and pre-decrements are cheaper.

For a `uint256 i` variable, the following is true with the Optimizer enabled at 10k:

**Increment:**

- `i += 1` is the most expensive form
- `i++` costs 6 gas less than `i += 1`
- `++i` costs 5 gas less than `i++` (11 gas less than `i += 1`)

**Decrement:**

- `i -= 1` is the most expensive form
- `i--` costs 11 gas less than `i -= 1`
- `--i` costs 5 gas less than `i--` (16 gas less than `i -= 1`)

Note that post-increments (or post-decrements) return the old value before incrementing or decrementing, hence the name *post-increment*:

```solidity
uint i = 1;  
uint j = 2;
require(j == i++, "This will be false as i is incremented after the comparison");
```
  
However, pre-increments (or pre-decrements) return the new value:
  
```solidity
uint i = 1;  
uint j = 2;
require(j == ++i, "This will be true as i is incremented before the comparison");
```

In the pre-increment case, the compiler has to create a temporary variable (when used) for returning `1` instead of `2`.

Consider using pre-increments and pre-decrements where they are relevant (meaning: not where post-increments/decrements logic are relevant).

*Saves 5 gas per instance*

*Instances (3)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

153:         _mint(params.recipient, (tokenId = _nextId++));

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

784:             if (amount0 == protocolFees.token0) amount0--; // ensure that the slot is not cleared, for gas savings

789:             if (amount1 == protocolFees.token1) amount1--; // ensure that the slot is not cleared, for gas savings

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="GAS-10"></a>[GAS-10] Using `private` rather than `public` for constants, saves gas

If needed, the values can be read from the verified contract source code, or if there are multiple values there can be a single getter function that [returns a tuple](https://github.com/code-423n4/2022-08-frax/blob/90f55a9ce4e25bceed3a74290b854341d8de6afa/src/contracts/FraxlendPair.sol#L156-L178) of the values of all currently-public constants. Saves **3406-3606 gas** in deployment gas due to the compiler not having to create non-payable getter functions for deployment calldata, not having to store the bytes of the value outside of where it's used, and not adding another entry to the method ID table

*Instances (3)*:

```solidity
File: contracts/ThrusterPool.sol

42:     IBlast public constant BLAST = IBlast(0x4300000000000000000000000000000000000002);

43:     IERC20Rebasing public constant USDB = IERC20Rebasing(0x4200000000000000000000000000000000000022);

44:     IERC20Rebasing public constant WETHB = IERC20Rebasing(0x4200000000000000000000000000000000000023);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="GAS-11"></a>[GAS-11] Splitting require() statements that use && saves gas

*Instances (6)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

266:         require(amount0 >= params.amount0Min && amount1 >= params.amount1Min, "Price slippage check");

364:         require(position.liquidity == 0 && position.tokensOwed0 == 0 && position.tokensOwed1 == 0, "Not cleared");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

152:         require(success && data.length >= 32);

162:         require(success && data.length >= 32);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

72:         require(msg.sender == owner && deployer == address(0), "INVALID");

83:         require(tickSpacing > 0 && tickSpacing < 16384);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="GAS-12"></a>[GAS-12] Use != 0 instead of > 0 for unsigned integer comparison

*Instances (24)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

256:         require(params.liquidity > 0);

303:         require(params.amount0Max > 0 || params.amount1Max > 0);

316:         if (position.liquidity > 0) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

438:         require(amount > 0);

453:         if (amount0 > 0) balance0Before = balance0();

454:         if (amount1 > 0) balance1Before = balance1();

456:         if (amount0 > 0) require(balance0Before.add(amount0) <= balance0(), "M0");

457:         if (amount1 > 0) require(balance1Before.add(amount1) <= balance1(), "M1");

476:         if (amount0 > 0) {

480:         if (amount1 > 0) {

508:         if (amount0 > 0 || amount1 > 0) {

601:         bool exactInput = amountSpecified > 0;

652:             if (cache.feeProtocol > 0) {

659:             if (state.liquidity > 0) {

731:             if (state.protocolFee > 0) protocolFees.token0 += state.protocolFee;

734:             if (state.protocolFee > 0) protocolFees.token1 += state.protocolFee;

749:             if (amount0 < 0) TransferHelper.safeTransfer(token0, recipient, uint256(-amount0));

766:             (feeProtocol0 == 0 || (feeProtocol0 >= 4 && feeProtocol0 <= 10))

783:         if (amount0 > 0) {

788:         if (amount1 > 0) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

83:         require(tickSpacing > 0 && tickSpacing < 16384);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

```solidity
File: contracts/base/PoolInitializer.sol

20:         require(token0 < token1);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/base/PoolInitializer.sol)

```solidity
File: contracts/libraries/PoolAddress.sol

2: pragma solidity >=0.5.0 <0.8.0;

30:         require(key.token0 < key.token1);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="GAS-13"></a>[GAS-13] `internal` functions not called by the contract should be removed

If the functions are required by an interface, the contract should inherit from that interface and use the `override` keyword

*Instances (2)*:

```solidity
File: contracts/libraries/PoolAddress.sol

20:     function getPoolKey(address tokenA, address tokenB, uint24 fee) internal pure returns (PoolKey memory) {

29:     function computeAddress(address factory, PoolKey memory key) internal pure returns (address pool) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="GAS-14"></a>[GAS-14] WETH address definition can be use directly

WETH is a wrap Ether contract with a specific address in the Ethereum network, giving the option to define it may cause false recognition, it is healthier to define it directly.

    Advantages of defining a specific contract directly:
    
    It saves gas,
    Prevents incorrect argument definition,
    Prevents execution on a different chain and re-signature issues,
    WETH Address : 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2

*Instances (2)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

75:         PeripheryImmutableState(_factory, _WETH9)

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

44:     IERC20Rebasing public constant WETHB = IERC20Rebasing(0x4200000000000000000000000000000000000023);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

## Non Critical Issues

| |Issue|Instances|
|-|:-|:-:|
| [NC-1](#NC-1) | Replace `abi.encodeWithSignature` and `abi.encodeWithSelector` with `abi.encodeCall` which keeps the code typo/type safe | 2 |
| [NC-2](#NC-2) | abicoder v2 is enabled by default | 1 |
| [NC-3](#NC-3) | Missing checks for `address(0)` when assigning values to address state variables | 6 |
| [NC-4](#NC-4) | Array indices should be referenced via `enum`s rather than via numeric literals | 3 |
| [NC-5](#NC-5) | Use `string.concat()` or `bytes.concat()` instead of `abi.encodePacked` | 1 |
| [NC-6](#NC-6) | `constant`s should be defined rather than using magic numbers | 14 |
| [NC-7](#NC-7) | Control structures do not follow the Solidity Style Guide | 27 |
| [NC-8](#NC-8) | Critical Changes Should Use Two-step Procedure | 1 |
| [NC-9](#NC-9) | Duplicated `require()`/`revert()` Checks Should Be Refactored To A Modifier Or Function | 4 |
| [NC-10](#NC-10) | Events that mark critical parameter changes should contain both the old and the new value | 2 |
| [NC-11](#NC-11) | Function ordering does not follow the Solidity style guide | 3 |
| [NC-12](#NC-12) | Functions should not be longer than 50 lines | 34 |
| [NC-13](#NC-13) | Lack of checks in setters | 1 |
| [NC-14](#NC-14) | Missing Event for critical parameters change | 2 |
| [NC-15](#NC-15) | NatSpec is completely non-existent on functions that should have them | 4 |
| [NC-16](#NC-16) | Use a `modifier` instead of a `require/if` statement for a special `msg.sender` actor | 8 |
| [NC-17](#NC-17) | Constant state variables defined more than once | 2 |
| [NC-18](#NC-18) | Consider using named mappings | 12 |
| [NC-19](#NC-19) | `address`s shouldn't be hard-coded | 4 |
| [NC-20](#NC-20) | Adding a `return` statement when the function defines a named return variable, is redundant | 5 |
| [NC-21](#NC-21) | `require()` / `revert()` statements should have descriptive reason strings | 25 |
| [NC-22](#NC-22) | Use scientific notation for readability reasons for large multiples of ten | 1 |
| [NC-23](#NC-23) | Contract does not follow the Solidity style guide's suggested layout ordering | 3 |
| [NC-24](#NC-24) | Some require descriptions are not clear | 11 |
| [NC-25](#NC-25) | Use Underscores for Number Literals (add an underscore every 3 digits) | 2 |
| [NC-26](#NC-26) | Internal and private variables and functions names should begin with an underscore | 6 |
| [NC-27](#NC-27) | Usage of floating `pragma` is not recommended | 1 |
| [NC-28](#NC-28) | Constants should be defined rather than using magic numbers | 2 |

### <a name="NC-1"></a>[NC-1] Replace `abi.encodeWithSignature` and `abi.encodeWithSelector` with `abi.encodeCall` which keeps the code typo/type safe

When using `abi.encodeWithSignature`, it is possible to include a typo for the correct function signature.
When using `abi.encodeWithSignature` or `abi.encodeWithSelector`, it is also possible to provide parameters that are not of the correct type for the function.

To avoid these pitfalls, it would be best to use [`abi.encodeCall`](https://solidity-by-example.org/abi-encode/) instead.

*Instances (2)*:

```solidity
File: contracts/ThrusterPool.sol

151:             token0.staticcall(abi.encodeWithSelector(IERC20Minimal.balanceOf.selector, address(this)));

161:             token1.staticcall(abi.encodeWithSelector(IERC20Minimal.balanceOf.selector, address(this)));

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="NC-2"></a>[NC-2] abicoder v2 is enabled by default

abicoder v2 is considered non-experimental as of Solidity 0.6.0 and it is enabled by default starting with Solidity 0.8.0. Therefore, there is no need to write.

*Instances (1)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

3: pragma abicoder v2;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

### <a name="NC-3"></a>[NC-3] Missing checks for `address(0)` when assigning values to address state variables

*Instances (6)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

78:         _tokenDescriptor = _tokenDescriptor_;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

799:         gauge = _gauge;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolDeployer.sol

30:         factory = _factory;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

30:         owner = _owner;

32:         pointsAdmin = _pointsAdmin;

73:         deployer = _deployer;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-4"></a>[NC-4] Array indices should be referenced via `enum`s rather than via numeric literals

*Instances (3)*:

```solidity
File: contracts/ThrusterPoolFactory.sol

34:         feeAmountTickSpacing[500] = 10;

36:         feeAmountTickSpacing[3000] = 60;

38:         feeAmountTickSpacing[10000] = 200;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-5"></a>[NC-5] Use `string.concat()` or `bytes.concat()` instead of `abi.encodePacked`

Solidity version 0.8.4 introduces `bytes.concat()` (vs `abi.encodePacked(<bytes>,<bytes>)`)

Solidity version 0.8.12 introduces `string.concat()` (vs `abi.encodePacked(<str>,<str>), which catches concatenation errors (in the event of a`bytes`data mixed in the concatenation)`)

*Instances (1)*:

```solidity
File: contracts/libraries/PoolAddress.sol

34:                     abi.encodePacked(

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="NC-6"></a>[NC-6] `constant`s should be defined rather than using magic numbers

Even [assembly](https://github.com/code-423n4/2022-05-opensea-seaport/blob/9d7ce4d08bf3c3010304a0476a785c70c0e90ae7/contracts/lib/TokenTransferrer.sol#L35-L39) can benefit from using readable constants instead of hex/numeric literals

*Instances (14)*:

```solidity
File: contracts/ThrusterPool.sol

152:         require(success && data.length >= 32);

162:         require(success && data.length >= 32);

591:             feeProtocol: zeroForOne ? (slot0Start.feeProtocol % 16) : (slot0Start.feeProtocol >> 4),

766:             (feeProtocol0 == 0 || (feeProtocol0 >= 4 && feeProtocol0 <= 10))

767:                 && (feeProtocol1 == 0 || (feeProtocol1 >= 4 && feeProtocol1 <= 10))

769:         slot0.feeProtocol = feeProtocol0 + (feeProtocol1 << 4);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

34:         feeAmountTickSpacing[500] = 10;

35:         emit FeeAmountEnabled(500, 10);

36:         feeAmountTickSpacing[3000] = 60;

37:         emit FeeAmountEnabled(3000, 60);

38:         feeAmountTickSpacing[10000] = 200;

39:         emit FeeAmountEnabled(10000, 200);

79:         require(fee < 1000000);

83:         require(tickSpacing > 0 && tickSpacing < 16384);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-7"></a>[NC-7] Control structures do not follow the Solidity Style Guide

See the [control structures](https://docs.soliditylang.org/en/latest/style-guide.html#control-structures) section of the Solidity Style Guide

*Instances (27)*:

```solidity
File: contracts/ThrusterPool.sol

304:     function _modifyPosition(ModifyPositionParams memory params)

439:         (, int256 amount0Int, int256 amount1Int) = _modifyPosition(

453:         if (amount0 > 0) balance0Before = balance0();

454:         if (amount1 > 0) balance1Before = balance1();

456:         if (amount0 > 0) require(balance0Before.add(amount0) <= balance0(), "M0");

457:         if (amount1 > 0) require(balance1Before.add(amount1) <= balance1(), "M1");

496:         (Position.Info storage position, int256 amount0Int, int256 amount1Int) = _modifyPosition(

534:         int256 amountSpecifiedRemaining;

570:         int256 amountSpecified,

574:         require(amountSpecified != 0, "AS");

601:         bool exactInput = amountSpecified > 0;

604:             amountSpecifiedRemaining: amountSpecified,

639:                 state.amountSpecifiedRemaining,

644:                 state.amountSpecifiedRemaining -= (step.amountIn + step.feeAmount).toInt256();

647:                 state.amountSpecifiedRemaining += step.amountOut.toInt256();

695:                     if (zeroForOne) liquidityNet = -liquidityNet;

725:         if (cache.liquidityStart != state.liquidity) liquidity = state.liquidity;

731:             if (state.protocolFee > 0) protocolFees.token0 += state.protocolFee;

734:             if (state.protocolFee > 0) protocolFees.token1 += state.protocolFee;

738:             ? (amountSpecified - state.amountSpecifiedRemaining, state.amountCalculated)

739:             : (state.amountCalculated, amountSpecified - state.amountSpecifiedRemaining);

743:             if (amount1 < 0) TransferHelper.safeTransfer(token1, recipient, uint256(-amount1));

749:             if (amount0 < 0) TransferHelper.safeTransfer(token0, recipient, uint256(-amount0));

784:             if (amount0 == protocolFees.token0) amount0--; // ensure that the slot is not cleared, for gas savings

789:             if (amount1 == protocolFees.token1) amount1--; // ensure that the slot is not cleared, for gas savings

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/base/PoolInitializer.sol

14:     function createAndInitializePoolIfNecessary(address token0, address token1, uint24 fee, uint160 sqrtPriceX96)

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/base/PoolInitializer.sol)

```solidity
File: contracts/libraries/PoolAddress.sol

21:         if (tokenA > tokenB) (tokenA, tokenB) = (tokenB, tokenA);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="NC-8"></a>[NC-8] Critical Changes Should Use Two-step Procedure

The critical procedures should be two step process.

See similar findings in previous Code4rena contests for reference: <https://code4rena.com/reports/2022-06-illuminate/#2-critical-changes-should-use-two-step-procedure>

**Recommended Mitigation Steps**

Lack of two-step procedure for critical operations leaves them error-prone. Consider adding two step procedure on the critical functions.

*Instances (1)*:

```solidity
File: contracts/ThrusterPoolFactory.sol

64:     function setOwner(address _owner) external override {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-9"></a>[NC-9] Duplicated `require()`/`revert()` Checks Should Be Refactored To A Modifier Or Function

*Instances (4)*:

```solidity
File: contracts/ThrusterPool.sol

115:         require(slot0.unlocked, "LOK");

578:         require(slot0Start.unlocked, "LOK");

747:             require(balance0Before.add(uint256(amount0)) <= balance0(), "IIA");

753:             require(balance1Before.add(uint256(amount1)) <= balance1(), "IIA");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="NC-10"></a>[NC-10] Events that mark critical parameter changes should contain both the old and the new value

This should especially be done if the new value is not required to be different from the old value

*Instances (2)*:

```solidity
File: contracts/ThrusterPool.sol

798:     function setGauge(address _gauge) external override lock onlyFactoryOwner {
             gauge = _gauge;
             emit SetGauge(_gauge);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

64:     function setOwner(address _owner) external override {
            require(msg.sender == owner);
            require(_owner != address(0));
            emit OwnerChanged(owner, _owner);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-11"></a>[NC-11] Function ordering does not follow the Solidity style guide

According to the [Solidity style guide](https://docs.soliditylang.org/en/v0.8.17/style-guide.html#order-of-functions), functions should be laid out in the following order :`constructor()`, `receive()`, `fallback()`, `external`, `public`, `internal`, `private`, but the cases below do not follow this pattern

*Instances (3)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

1: 
   Current order:
   external positions
   private cachePoolKey
   external mint
   public tokenURI
   public baseURI
   external increaseLiquidity
   external decreaseLiquidity
   external collect
   external burn
   internal _getAndIncrementNonce
   public getApproved
   internal _approve
   
   Suggested order:
   external positions
   external mint
   external increaseLiquidity
   external decreaseLiquidity
   external collect
   external burn
   public tokenURI
   public baseURI
   public getApproved
   internal _getAndIncrementNonce
   internal _approve
   private cachePoolKey

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

1: 
   Current order:
   private checkTicks
   private balance0
   private balance1
   external snapshotCumulativesInside
   external observe
   external increaseObservationCardinalityNext
   external initialize
   private _modifyPosition
   private _updatePosition
   external mint
   external collect
   external burn
   external swap
   external setFeeProtocol
   external collectProtocol
   external setGauge
   external claimYieldAll
   external blastPointsAdmin
   
   Suggested order:
   external snapshotCumulativesInside
   external observe
   external increaseObservationCardinalityNext
   external initialize
   external mint
   external collect
   external burn
   external swap
   external setFeeProtocol
   external collectProtocol
   external setGauge
   external claimYieldAll
   external blastPointsAdmin
   private checkTicks
   private balance0
   private balance1
   private _modifyPosition
   private _updatePosition

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

1: 
   Current order:
   public createPool
   external setOwner
   external setDeployer
   public enableFeeAmount
   external claimDeployerGas
   external emitSwap
   
   Suggested order:
   external setOwner
   external setDeployer
   external claimDeployerGas
   external emitSwap
   public createPool
   public enableFeeAmount

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-12"></a>[NC-12] Functions should not be longer than 50 lines

Overly complex code can make understanding functionality more difficult, try to further modularize your code to ensure readability

*Instances (34)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

121:     function cachePoolKey(address pool, PoolAddress.PoolKey memory poolKey) private returns (uint80 poolId) {

186:     function tokenURI(uint256 tokenId) public view override(ERC721, IERC721Metadata) returns (string memory) {

192:     function baseURI() public pure override returns (string memory) {}

195:     function increaseLiquidity(IncreaseLiquidityParams calldata params)

248:     function decreaseLiquidity(DecreaseLiquidityParams calldata params)

362:     function burn(uint256 tokenId) external payable override isAuthorizedForToken(tokenId) {

369:     function _getAndIncrementNonce(uint256 tokenId) internal override returns (uint256) {

374:     function getApproved(uint256 tokenId) public view override(ERC721, IERC721) returns (address) {

381:     function _approve(address to, uint256 tokenId) internal override(ERC721) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

140:     function checkTicks(int24 tickLower, int24 tickUpper) private pure {

149:     function balance0() private view returns (uint256) {

159:     function balance1() private view returns (uint256) {

167:     function snapshotCumulativesInside(int24 tickLower, int24 tickUpper)

252:     function increaseObservationCardinalityNext(uint16 observationCardinalityNext)

269:     function initialize(uint160 sqrtPriceX96) external override {

304:     function _modifyPosition(ModifyPositionParams memory params)

363:     function _updatePosition(address owner, int24 tickLower, int24 tickUpper, int128 liquidityDelta, int24 tick)

432:     function mint(address recipient, int24 tickLower, int24 tickUpper, uint128 amount, bytes calldata data)

490:     function burn(int24 tickLower, int24 tickUpper, uint128 amount)

764:     function setFeeProtocol(uint8 feeProtocol0, uint8 feeProtocol1) external override lock onlyFactoryOwner {

773:     function collectProtocol(address recipient, uint128 amount0Requested, uint128 amount1Requested)

798:     function setGauge(address _gauge) external override lock onlyFactoryOwner {

804:     function claimYieldAll(address _recipient, uint256 _amountETH, uint256 _amountWETH, uint256 _amountUSDB)

816:     function blastPointsAdmin() external view override returns (address) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolDeployer.sol

34:     function deploy(address _factory, address token0, address token1, uint24 fee, int24 tickSpacing)

45:     function claimGas(address _recipient) external override onlyFactory returns (uint256 amount) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

43:     function createPool(address tokenA, address tokenB, uint24 fee)

64:     function setOwner(address _owner) external override {

71:     function setDeployer(address _deployer) external {

77:     function enableFeeAmount(uint24 fee, int24 tickSpacing) public override {

90:     function claimDeployerGas(address _recipient) external {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

```solidity
File: contracts/base/PoolInitializer.sol

14:     function createAndInitializePoolIfNecessary(address token0, address token1, uint24 fee, uint160 sqrtPriceX96)

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/base/PoolInitializer.sol)

```solidity
File: contracts/libraries/PoolAddress.sol

20:     function getPoolKey(address tokenA, address tokenB, uint24 fee) internal pure returns (PoolKey memory) {

29:     function computeAddress(address factory, PoolKey memory key) internal pure returns (address pool) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="NC-13"></a>[NC-13] Lack of checks in setters

Be it sanity checks (like checks against `0`-values) or initial setting checks: it's best for Setter functions to have them

*Instances (1)*:

```solidity
File: contracts/ThrusterPool.sol

798:     function setGauge(address _gauge) external override lock onlyFactoryOwner {
             gauge = _gauge;
             emit SetGauge(_gauge);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="NC-14"></a>[NC-14] Missing Event for critical parameters change

Events help non-contract tools to track changes, and events prevent users from being surprised by changes.

*Instances (2)*:

```solidity
File: contracts/ThrusterPool.sol

764:     function setFeeProtocol(uint8 feeProtocol0, uint8 feeProtocol1) external override lock onlyFactoryOwner {
             require(
                 (feeProtocol0 == 0 || (feeProtocol0 >= 4 && feeProtocol0 <= 10))
                     && (feeProtocol1 == 0 || (feeProtocol1 >= 4 && feeProtocol1 <= 10))
             );
             slot0.feeProtocol = feeProtocol0 + (feeProtocol1 << 4);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

71:     function setDeployer(address _deployer) external {
            require(msg.sender == owner && deployer == address(0), "INVALID");
            deployer = _deployer;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-15"></a>[NC-15] NatSpec is completely non-existent on functions that should have them

Public and external functions that aren't view or pure should have NatSpec comments

*Instances (4)*:

```solidity
File: contracts/ThrusterPoolDeployer.sol

45:     function claimGas(address _recipient) external override onlyFactory returns (uint256 amount) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

71:     function setDeployer(address _deployer) external {

90:     function claimDeployerGas(address _recipient) external {

95:     function emitSwap(

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-16"></a>[NC-16] Use a `modifier` instead of a `require/if` statement for a special `msg.sender` actor

If a function is supposed to be access-controlled, a `modifier` should be used instead of a `require/if` statement for more readability.

*Instances (8)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

182:         require(_isApprovedOrOwner(msg.sender, tokenId), "Not approved");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

123:         require(msg.sender == IThrusterPoolFactory(factory).owner());

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolDeployer.sol

24:         require(msg.sender == factory);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

65:         require(msg.sender == owner);

72:         require(msg.sender == owner && deployer == address(0), "INVALID");

78:         require(msg.sender == owner);

91:         require(msg.sender == owner);

104:         require(poolExists[msg.sender], "INVALID_POOL");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-17"></a>[NC-17] Constant state variables defined more than once

Rather than redefining state variable constant, consider using a library to store all constants as this will prevent data redundancy

*Instances (2)*:

```solidity
File: contracts/ThrusterPool.sol

42:     IBlast public constant BLAST = IBlast(0x4300000000000000000000000000000000000002);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolDeployer.sol

21:     address private constant BLAST = 0x4300000000000000000000000000000000000002;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

### <a name="NC-18"></a>[NC-18] Consider using named mappings

Consider moving to solidity version 0.8.18 or later, and using [named mappings](https://ethereum.stackexchange.com/questions/51629/how-to-name-the-arguments-in-mapping/145555#145555) to make it easier to understand the purpose of each mapping

*Instances (12)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

57:     mapping(address => uint80) private _poolIds;

60:     mapping(uint80 => PoolAddress.PoolKey) private _poolIdToPoolKey;

63:     mapping(uint256 => Position) private _positions;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

36:     using Tick for mapping(int24 => Tick.Info);

37:     using TickBitmap for mapping(int16 => uint256);

38:     using Position for mapping(bytes32 => Position.Info);

100:     mapping(int24 => Tick.Info) public override ticks;

102:     mapping(int16 => uint256) public override tickBitmap;

104:     mapping(bytes32 => Position.Info) public override positions;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

24:     mapping(uint24 => int24) public override feeAmountTickSpacing;

26:     mapping(address => mapping(address => mapping(uint24 => address))) public override getPool;

27:     mapping(address => bool) public poolExists;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-19"></a>[NC-19] `address`s shouldn't be hard-coded

It is often better to declare `address`es as `immutable`, and assign them via constructor arguments. This allows the code to remain the same across deployments on different networks, and avoids recompilation when addresses need to change.

*Instances (4)*:

```solidity
File: contracts/ThrusterPool.sol

42:     IBlast public constant BLAST = IBlast(0x4300000000000000000000000000000000000002);

43:     IERC20Rebasing public constant USDB = IERC20Rebasing(0x4200000000000000000000000000000000000022);

44:     IERC20Rebasing public constant WETHB = IERC20Rebasing(0x4200000000000000000000000000000000000023);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolDeployer.sol

21:     address private constant BLAST = 0x4300000000000000000000000000000000000002;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

### <a name="NC-20"></a>[NC-20] Adding a `return` statement when the function defines a named return variable, is redundant

*Instances (5)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

81:     /// @inheritdoc INonfungiblePositionManager
        function positions(uint256 tokenId)
            external
            view
            override
            returns (
                uint96 nonce,
                address operator,
                address token0,
                address token1,
                uint24 fee,
                int24 tickLower,
                int24 tickUpper,
                uint128 liquidity,
                uint256 feeGrowthInside0LastX128,
                uint256 feeGrowthInside1LastX128,
                uint128 tokensOwed0,
                uint128 tokensOwed1
            )
        {
            Position memory position = _positions[tokenId];
            require(position.poolId != 0, "Invalid token ID");
            PoolAddress.PoolKey memory poolKey = _poolIdToPoolKey[position.poolId];
            return (

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

166:     /// @inheritdoc IThrusterPoolDerivedState
         function snapshotCumulativesInside(int24 tickLower, int24 tickUpper)
             external
             view
             override
             noDelegateCall
             returns (int56 tickCumulativeInside, uint160 secondsPerLiquidityInsideX128, uint32 secondsInside)
         {
             checkTicks(tickLower, tickUpper);
     
             int56 tickCumulativeLower;
             int56 tickCumulativeUpper;
             uint160 secondsPerLiquidityOutsideLowerX128;
             uint160 secondsPerLiquidityOutsideUpperX128;
             uint32 secondsOutsideLower;
             uint32 secondsOutsideUpper;
     
             {
                 Tick.Info storage lower = ticks[tickLower];
                 Tick.Info storage upper = ticks[tickUpper];
                 bool initializedLower;
                 (tickCumulativeLower, secondsPerLiquidityOutsideLowerX128, secondsOutsideLower, initializedLower) = (
                     lower.tickCumulativeOutside,
                     lower.secondsPerLiquidityOutsideX128,
                     lower.secondsOutside,
                     lower.initialized
                 );
                 require(initializedLower);
     
                 bool initializedUpper;
                 (tickCumulativeUpper, secondsPerLiquidityOutsideUpperX128, secondsOutsideUpper, initializedUpper) = (
                     upper.tickCumulativeOutside,
                     upper.secondsPerLiquidityOutsideX128,
                     upper.secondsOutside,
                     upper.initialized
                 );
                 require(initializedUpper);
             }
     
             Slot0 memory _slot0 = slot0;
     
             if (_slot0.tick < tickLower) {
                 return (

166:     /// @inheritdoc IThrusterPoolDerivedState
         function snapshotCumulativesInside(int24 tickLower, int24 tickUpper)
             external
             view
             override
             noDelegateCall
             returns (int56 tickCumulativeInside, uint160 secondsPerLiquidityInsideX128, uint32 secondsInside)
         {
             checkTicks(tickLower, tickUpper);
     
             int56 tickCumulativeLower;
             int56 tickCumulativeUpper;
             uint160 secondsPerLiquidityOutsideLowerX128;
             uint160 secondsPerLiquidityOutsideUpperX128;
             uint32 secondsOutsideLower;
             uint32 secondsOutsideUpper;
     
             {
                 Tick.Info storage lower = ticks[tickLower];
                 Tick.Info storage upper = ticks[tickUpper];
                 bool initializedLower;
                 (tickCumulativeLower, secondsPerLiquidityOutsideLowerX128, secondsOutsideLower, initializedLower) = (
                     lower.tickCumulativeOutside,
                     lower.secondsPerLiquidityOutsideX128,
                     lower.secondsOutside,
                     lower.initialized
                 );
                 require(initializedLower);
     
                 bool initializedUpper;
                 (tickCumulativeUpper, secondsPerLiquidityOutsideUpperX128, secondsOutsideUpper, initializedUpper) = (
                     upper.tickCumulativeOutside,
                     upper.secondsPerLiquidityOutsideX128,
                     upper.secondsOutside,
                     upper.initialized
                 );
                 require(initializedUpper);
             }
     
             Slot0 memory _slot0 = slot0;
     
             if (_slot0.tick < tickLower) {
                 return (
                     tickCumulativeLower - tickCumulativeUpper,
                     secondsPerLiquidityOutsideLowerX128 - secondsPerLiquidityOutsideUpperX128,
                     secondsOutsideLower - secondsOutsideUpper
                 );
             } else if (_slot0.tick < tickUpper) {
                 uint32 time = uint32(block.timestamp);
                 (int56 tickCumulative, uint160 secondsPerLiquidityCumulativeX128) = observations.observeSingle(
                     time, 0, _slot0.tick, _slot0.observationIndex, liquidity, _slot0.observationCardinality
                 );
                 return (
                     tickCumulative - tickCumulativeLower - tickCumulativeUpper,
                     secondsPerLiquidityCumulativeX128 - secondsPerLiquidityOutsideLowerX128
                         - secondsPerLiquidityOutsideUpperX128,
                     time - secondsOutsideLower - secondsOutsideUpper
                 );
             } else {
                 return (

166:     /// @inheritdoc IThrusterPoolDerivedState
         function snapshotCumulativesInside(int24 tickLower, int24 tickUpper)
             external
             view
             override
             noDelegateCall
             returns (int56 tickCumulativeInside, uint160 secondsPerLiquidityInsideX128, uint32 secondsInside)
         {
             checkTicks(tickLower, tickUpper);
     
             int56 tickCumulativeLower;
             int56 tickCumulativeUpper;
             uint160 secondsPerLiquidityOutsideLowerX128;
             uint160 secondsPerLiquidityOutsideUpperX128;
             uint32 secondsOutsideLower;
             uint32 secondsOutsideUpper;
     
             {
                 Tick.Info storage lower = ticks[tickLower];
                 Tick.Info storage upper = ticks[tickUpper];
                 bool initializedLower;
                 (tickCumulativeLower, secondsPerLiquidityOutsideLowerX128, secondsOutsideLower, initializedLower) = (
                     lower.tickCumulativeOutside,
                     lower.secondsPerLiquidityOutsideX128,
                     lower.secondsOutside,
                     lower.initialized
                 );
                 require(initializedLower);
     
                 bool initializedUpper;
                 (tickCumulativeUpper, secondsPerLiquidityOutsideUpperX128, secondsOutsideUpper, initializedUpper) = (
                     upper.tickCumulativeOutside,
                     upper.secondsPerLiquidityOutsideX128,
                     upper.secondsOutside,
                     upper.initialized
                 );
                 require(initializedUpper);
             }
     
             Slot0 memory _slot0 = slot0;
     
             if (_slot0.tick < tickLower) {
                 return (
                     tickCumulativeLower - tickCumulativeUpper,
                     secondsPerLiquidityOutsideLowerX128 - secondsPerLiquidityOutsideUpperX128,
                     secondsOutsideLower - secondsOutsideUpper
                 );
             } else if (_slot0.tick < tickUpper) {
                 uint32 time = uint32(block.timestamp);
                 (int56 tickCumulative, uint160 secondsPerLiquidityCumulativeX128) = observations.observeSingle(
                     time, 0, _slot0.tick, _slot0.observationIndex, liquidity, _slot0.observationCardinality
                 );
                 return (

233:     /// @inheritdoc IThrusterPoolDerivedState
         function observe(uint32[] calldata secondsAgos)
             external
             view
             override
             noDelegateCall
             returns (int56[] memory tickCumulatives, uint160[] memory secondsPerLiquidityCumulativeX128s)
         {
             return observations.observe(

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="NC-21"></a>[NC-21] `require()` / `revert()` statements should have descriptive reason strings

*Instances (25)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

187:         require(_exists(tokenId));

256:         require(params.liquidity > 0);

260:         require(positionLiquidity >= params.liquidity);

303:         require(params.amount0Max > 0 || params.amount1Max > 0);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

123:         require(msg.sender == IThrusterPoolFactory(factory).owner());

152:         require(success && data.length >= 32);

162:         require(success && data.length >= 32);

193:             require(initializedLower);

202:             require(initializedUpper);

438:         require(amount > 0);

765:         require(

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolDeployer.sol

24:         require(msg.sender == factory);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

49:         require(tokenA != tokenB);

51:         require(token0 != address(0));

53:         require(tickSpacing != 0);

54:         require(getPool[token0][token1][fee] == address(0));

65:         require(msg.sender == owner);

66:         require(_owner != address(0));

78:         require(msg.sender == owner);

79:         require(fee < 1000000);

83:         require(tickSpacing > 0 && tickSpacing < 16384);

84:         require(feeAmountTickSpacing[fee] == 0);

91:         require(msg.sender == owner);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

```solidity
File: contracts/base/PoolInitializer.sol

20:         require(token0 < token1);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/base/PoolInitializer.sol)

```solidity
File: contracts/libraries/PoolAddress.sol

30:         require(key.token0 < key.token1);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="NC-22"></a>[NC-22] Use scientific notation for readability reasons for large multiples of ten

The more a number has zeros, the harder it becomes to see with the eyes if it's the intended value. To ease auditing and bug bounty hunting, consider using the scientific notation

*Instances (1)*:

```solidity
File: contracts/ThrusterPoolFactory.sol

79:         require(fee < 1000000);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-23"></a>[NC-23] Contract does not follow the Solidity style guide's suggested layout ordering

The [style guide](https://docs.soliditylang.org/en/v0.8.16/style-guide.html#order-of-layout) says that, within a contract, the ordering should be:

1) Type declarations
2) State variables
3) Events
4) Modifiers
5) Functions

However, the contract(s) below do not follow this ordering

*Instances (3)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

1: 
   Current order:
   StructDefinition.Position
   VariableDeclaration._poolIds
   VariableDeclaration._poolIdToPoolKey
   VariableDeclaration._positions
   VariableDeclaration._nextId
   VariableDeclaration._nextPoolId
   VariableDeclaration._tokenDescriptor
   FunctionDefinition.constructor
   FunctionDefinition.positions
   FunctionDefinition.cachePoolKey
   FunctionDefinition.mint
   ModifierDefinition.isAuthorizedForToken
   FunctionDefinition.tokenURI
   FunctionDefinition.baseURI
   FunctionDefinition.increaseLiquidity
   FunctionDefinition.decreaseLiquidity
   FunctionDefinition.collect
   FunctionDefinition.burn
   FunctionDefinition._getAndIncrementNonce
   FunctionDefinition.getApproved
   FunctionDefinition._approve
   
   Suggested order:
   VariableDeclaration._poolIds
   VariableDeclaration._poolIdToPoolKey
   VariableDeclaration._positions
   VariableDeclaration._nextId
   VariableDeclaration._nextPoolId
   VariableDeclaration._tokenDescriptor
   StructDefinition.Position
   ModifierDefinition.isAuthorizedForToken
   FunctionDefinition.constructor
   FunctionDefinition.positions
   FunctionDefinition.cachePoolKey
   FunctionDefinition.mint
   FunctionDefinition.tokenURI
   FunctionDefinition.baseURI
   FunctionDefinition.increaseLiquidity
   FunctionDefinition.decreaseLiquidity
   FunctionDefinition.collect
   FunctionDefinition.burn
   FunctionDefinition._getAndIncrementNonce
   FunctionDefinition.getApproved
   FunctionDefinition._approve

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

1: 
   Current order:
   UsingForDirective.LowGasSafeMath
   UsingForDirective.LowGasSafeMath
   UsingForDirective.SafeCast
   UsingForDirective.SafeCast
   UsingForDirective.Tick
   UsingForDirective.TickBitmap
   UsingForDirective.Position
   UsingForDirective.Position
   UsingForDirective.Oracle
   VariableDeclaration.BLAST
   VariableDeclaration.USDB
   VariableDeclaration.WETHB
   VariableDeclaration.factory
   VariableDeclaration.token0
   VariableDeclaration.token1
   VariableDeclaration.fee
   VariableDeclaration.tickSpacing
   VariableDeclaration.maxLiquidityPerTick
   StructDefinition.Slot0
   VariableDeclaration.slot0
   VariableDeclaration.feeGrowthGlobal0X128
   VariableDeclaration.feeGrowthGlobal1X128
   StructDefinition.ProtocolFees
   VariableDeclaration.protocolFees
   VariableDeclaration.liquidity
   VariableDeclaration.ticks
   VariableDeclaration.tickBitmap
   VariableDeclaration.positions
   VariableDeclaration.observations
   VariableDeclaration.gauge
   ModifierDefinition.lock
   ModifierDefinition.onlyFactoryOwner
   FunctionDefinition.constructor
   FunctionDefinition.checkTicks
   FunctionDefinition.balance0
   FunctionDefinition.balance1
   FunctionDefinition.snapshotCumulativesInside
   FunctionDefinition.observe
   FunctionDefinition.increaseObservationCardinalityNext
   FunctionDefinition.initialize
   StructDefinition.ModifyPositionParams
   FunctionDefinition._modifyPosition
   FunctionDefinition._updatePosition
   FunctionDefinition.mint
   FunctionDefinition.collect
   FunctionDefinition.burn
   StructDefinition.SwapCache
   StructDefinition.SwapState
   StructDefinition.StepComputations
   FunctionDefinition.swap
   FunctionDefinition.setFeeProtocol
   FunctionDefinition.collectProtocol
   FunctionDefinition.setGauge
   FunctionDefinition.claimYieldAll
   FunctionDefinition.blastPointsAdmin
   
   Suggested order:
   UsingForDirective.LowGasSafeMath
   UsingForDirective.LowGasSafeMath
   UsingForDirective.SafeCast
   UsingForDirective.SafeCast
   UsingForDirective.Tick
   UsingForDirective.TickBitmap
   UsingForDirective.Position
   UsingForDirective.Position
   UsingForDirective.Oracle
   VariableDeclaration.BLAST
   VariableDeclaration.USDB
   VariableDeclaration.WETHB
   VariableDeclaration.factory
   VariableDeclaration.token0
   VariableDeclaration.token1
   VariableDeclaration.fee
   VariableDeclaration.tickSpacing
   VariableDeclaration.maxLiquidityPerTick
   VariableDeclaration.slot0
   VariableDeclaration.feeGrowthGlobal0X128
   VariableDeclaration.feeGrowthGlobal1X128
   VariableDeclaration.protocolFees
   VariableDeclaration.liquidity
   VariableDeclaration.ticks
   VariableDeclaration.tickBitmap
   VariableDeclaration.positions
   VariableDeclaration.observations
   VariableDeclaration.gauge
   StructDefinition.Slot0
   StructDefinition.ProtocolFees
   StructDefinition.ModifyPositionParams
   StructDefinition.SwapCache
   StructDefinition.SwapState
   StructDefinition.StepComputations
   ModifierDefinition.lock
   ModifierDefinition.onlyFactoryOwner
   FunctionDefinition.constructor
   FunctionDefinition.checkTicks
   FunctionDefinition.balance0
   FunctionDefinition.balance1
   FunctionDefinition.snapshotCumulativesInside
   FunctionDefinition.observe
   FunctionDefinition.increaseObservationCardinalityNext
   FunctionDefinition.initialize
   FunctionDefinition._modifyPosition
   FunctionDefinition._updatePosition
   FunctionDefinition.mint
   FunctionDefinition.collect
   FunctionDefinition.burn
   FunctionDefinition.swap
   FunctionDefinition.setFeeProtocol
   FunctionDefinition.collectProtocol
   FunctionDefinition.setGauge
   FunctionDefinition.claimYieldAll
   FunctionDefinition.blastPointsAdmin

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolDeployer.sol

1: 
   Current order:
   StructDefinition.Parameters
   VariableDeclaration.parameters
   VariableDeclaration.factory
   VariableDeclaration.BLAST
   ModifierDefinition.onlyFactory
   FunctionDefinition.constructor
   FunctionDefinition.deploy
   FunctionDefinition.claimGas
   
   Suggested order:
   VariableDeclaration.parameters
   VariableDeclaration.factory
   VariableDeclaration.BLAST
   StructDefinition.Parameters
   ModifierDefinition.onlyFactory
   FunctionDefinition.constructor
   FunctionDefinition.deploy
   FunctionDefinition.claimGas

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

### <a name="NC-24"></a>[NC-24] Some require descriptions are not clear

1. It does not comply with the general require error description model of the project (Either all of them should be debugged in this way, or all of them should be explained with a string not exceeding 32 bytes.)
2. For debug dapps like Tenderly, these debug messages are important, this allows the user to see the reasons for revert practically.

*Instances (11)*:

```solidity
File: contracts/ThrusterPool.sol

115:         require(slot0.unlocked, "LOK");

141:         require(tickLower < tickUpper, "TLU");

142:         require(tickLower >= TickMath.MIN_TICK, "TLM");

143:         require(tickUpper <= TickMath.MAX_TICK, "TUM");

270:         require(slot0.sqrtPriceX96 == 0, "AI");

456:         if (amount0 > 0) require(balance0Before.add(amount0) <= balance0(), "M0");

457:         if (amount1 > 0) require(balance1Before.add(amount1) <= balance1(), "M1");

574:         require(amountSpecified != 0, "AS");

578:         require(slot0Start.unlocked, "LOK");

747:             require(balance0Before.add(uint256(amount0)) <= balance0(), "IIA");

753:             require(balance1Before.add(uint256(amount1)) <= balance1(), "IIA");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="NC-25"></a>[NC-25] Use Underscores for Number Literals (add an underscore every 3 digits)

*Instances (2)*:

```solidity
File: contracts/ThrusterPoolFactory.sol

79:         require(fee < 1000000);

83:         require(tickSpacing > 0 && tickSpacing < 16384);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="NC-26"></a>[NC-26] Internal and private variables and functions names should begin with an underscore

According to the Solidity Style Guide, Non-`external` variable and function names should begin with an [underscore](https://docs.soliditylang.org/en/latest/style-guide.html#underscore-prefix-for-non-external-functions-and-variables)

*Instances (6)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

121:     function cachePoolKey(address pool, PoolAddress.PoolKey memory poolKey) private returns (uint80 poolId) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

140:     function checkTicks(int24 tickLower, int24 tickUpper) private pure {

149:     function balance0() private view returns (uint256) {

159:     function balance1() private view returns (uint256) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/libraries/PoolAddress.sol

20:     function getPoolKey(address tokenA, address tokenB, uint24 fee) internal pure returns (PoolKey memory) {

29:     function computeAddress(address factory, PoolKey memory key) internal pure returns (address pool) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="NC-27"></a>[NC-27] Usage of floating `pragma` is not recommended

*Instances (1)*:

```solidity
File: contracts/libraries/PoolAddress.sol

2: pragma solidity >=0.5.0 <0.8.0;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="NC-28"></a>[NC-28] Constants should be defined rather than using magic numbers

*Instances (2)*:

```solidity
File: contracts/ThrusterPoolFactory.sol

35:         emit FeeAmountEnabled(500, 10);

37:         emit FeeAmountEnabled(3000, 60);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

## Low Issues

| |Issue|Instances|
|-|:-|:-:|
| [L-1](#L-1) | Missing checks for `address(0)` when assigning values to address state variables | 6 |
| [L-2](#L-2) | `abi.encodePacked()` should not be used with dynamic types when passing the result to a hash function such as `keccak256()` | 1 |
| [L-3](#L-3) | Do not leave an implementation contract uninitialized | 1 |
| [L-4](#L-4) | Division by zero not prevented | 1 |
| [L-5](#L-5) | Empty Function Body - Consider commenting why | 1 |
| [L-6](#L-6) | Initializers could be front-run | 4 |
| [L-7](#L-7) | Prevent accidentally burning tokens | 2 |
| [L-8](#L-8) | Solidity version 0.8.20+ may not work on other chains due to `PUSH0` | 1 |
| [L-9](#L-9) | File allows a version of solidity that is susceptible to an assembly optimizer bug | 1 |
| [L-10](#L-10) | Consider using OpenZeppelin's SafeCast library to prevent unexpected overflows when downcasting | 10 |
| [L-11](#L-11) | Unspecific compiler version pragma | 1 |
| [L-12](#L-12) | Upgradeable contract not initialized | 22 |

### <a name="L-1"></a>[L-1] Missing checks for `address(0)` when assigning values to address state variables

*Instances (6)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

78:         _tokenDescriptor = _tokenDescriptor_;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

799:         gauge = _gauge;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/ThrusterPoolDeployer.sol

30:         factory = _factory;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolDeployer.sol)

```solidity
File: contracts/ThrusterPoolFactory.sol

30:         owner = _owner;

32:         pointsAdmin = _pointsAdmin;

73:         deployer = _deployer;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPoolFactory.sol)

### <a name="L-2"></a>[L-2] `abi.encodePacked()` should not be used with dynamic types when passing the result to a hash function such as `keccak256()`

Use `abi.encode()` instead which will pad items to 32 bytes, which will [prevent hash collisions](https://docs.soliditylang.org/en/v0.8.13/abi-spec.html#non-standard-packed-mode) (e.g. `abi.encodePacked(0x123,0x456)` => `0x123456` => `abi.encodePacked(0x1,0x23456)`, but `abi.encode(0x123,0x456)` => `0x0...1230...456`). "Unless there is a compelling reason, `abi.encode` should be preferred". If there is only one argument to `abi.encodePacked()` it can often be cast to `bytes()` or `bytes32()` [instead](https://ethereum.stackexchange.com/questions/30912/how-to-compare-strings-in-solidity#answer-82739).
If all arguments are strings and or bytes, `bytes.concat()` should be used instead

*Instances (1)*:

```solidity
File: contracts/libraries/PoolAddress.sol

35:                         hex"ff", factory, keccak256(abi.encode(key.token0, key.token1, key.fee)), POOL_INIT_CODE_HASH

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="L-3"></a>[L-3] Do not leave an implementation contract uninitialized

An uninitialized implementation contract can be taken over by an attacker, which may impact the proxy. To prevent the implementation contract from being used, it's advisable to invoke the `_disableInitializers` function in the constructor to automatically lock it when it is deployed. This should look similar to this:

```solidity
  /// @custom:oz-upgrades-unsafe-allow constructor
  constructor() {
      _disableInitializers();
  }
```

Sources:

- <https://docs.openzeppelin.com/contracts/4.x/api/proxy#Initializable-_disableInitializers-->
- <https://twitter.com/0xCygaar/status/1621417995905167360?s=20>

*Instances (1)*:

```solidity
File: contracts/ThrusterPool.sol

127:     constructor() {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="L-4"></a>[L-4] Division by zero not prevented

The divisions below take an input parameter which does not have any zero-value checks, which may lead to the functions reverting when zero is passed.

*Instances (1)*:

```solidity
File: contracts/ThrusterPool.sol

653:                 uint256 delta = step.feeAmount / cache.feeProtocol;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="L-5"></a>[L-5] Empty Function Body - Consider commenting why

*Instances (1)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

192:     function baseURI() public pure override returns (string memory) {}

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

### <a name="L-6"></a>[L-6] Initializers could be front-run

Initializers could be front-run, allowing an attacker to either set their own values, take ownership of the contract, and in the best case forcing a re-deployment

*Instances (4)*:

```solidity
File: contracts/ThrusterPool.sol

269:     function initialize(uint160 sqrtPriceX96) external override {

274:         (uint16 cardinality, uint16 cardinalityNext) = observations.initialize(uint32(block.timestamp));

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/base/PoolInitializer.sol

25:             IThrusterPool(pool).initialize(sqrtPriceX96);

29:                 IThrusterPool(pool).initialize(sqrtPriceX96);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/base/PoolInitializer.sol)

### <a name="L-7"></a>[L-7] Prevent accidentally burning tokens

Minting and burning tokens to address(0) prevention

*Instances (2)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

153:         _mint(params.recipient, (tokenId = _nextId++));

366:         _burn(tokenId);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

### <a name="L-8"></a>[L-8] Solidity version 0.8.20+ may not work on other chains due to `PUSH0`

The compiler for Solidity 0.8.20 switches the default target EVM version to [Shanghai](https://blog.soliditylang.org/2023/05/10/solidity-0.8.20-release-announcement/#important-note), which includes the new `PUSH0` op code. This op code may not yet be implemented on all L2s, so deployment on these chains will fail. To work around this issue, use an earlier [EVM](https://docs.soliditylang.org/en/v0.8.20/using-the-compiler.html?ref=zaryabs.com#setting-the-evm-version-to-target) [version](https://book.getfoundry.sh/reference/config/solidity-compiler#evm_version). While the project itself may or may not compile with 0.8.20, other projects with which it integrates, or which extend this project may, and those projects will have problems deploying these contracts/libraries.

*Instances (1)*:

```solidity
File: contracts/libraries/PoolAddress.sol

2: pragma solidity >=0.5.0 <0.8.0;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="L-9"></a>[L-9] File allows a version of solidity that is susceptible to an assembly optimizer bug

In solidity versions 0.8.13 and 0.8.14, there is an [optimizer bug](https://github.com/ethereum/solidity-blog/blob/499ab8abc19391be7b7b34f88953a067029a5b45/_posts/2022-06-15-inline-assembly-memory-side-effects-bug.md) where, if the use of a variable is in a separate `assembly` block from the block in which it was stored, the `mstore` operation is optimized out, leading to uninitialized memory. The code currently does not have such a pattern of execution, but it does use `mstore`s in `assembly` blocks, so it is a risk for future changes. The affected solidity versions should be avoided if at all possible.

*Instances (1)*:

```solidity
File: contracts/libraries/PoolAddress.sol

2: pragma solidity >=0.5.0 <0.8.0;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="L-10"></a>[L-10] Consider using OpenZeppelin's SafeCast library to prevent unexpected overflows when downcasting

Downcasting from `uint256`/`int256` in Solidity does not revert on overflow. This can result in undesired exploitation or bugs, since developers usually assume that overflows raise errors. [OpenZeppelin's SafeCast library](https://docs.openzeppelin.com/contracts/3.x/api/utils#SafeCast) restores this intuition by reverting the transaction when such an operation overflows. Using this library eliminates an entire class of bugs, so it's recommended to use it always. Some exceptions are acceptable like with the classic `uint256(uint160(address(variable)))`

*Instances (10)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

227:         position.tokensOwed0 += uint128(

232:         position.tokensOwed1 += uint128(

272:         position.tokensOwed0 += uint128(amount0)

273:             + uint128(

278:         position.tokensOwed1 += uint128(amount1)

279:             + uint128(

321:             tokensOwed0 += uint128(

326:             tokensOwed1 += uint128(

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

510:                 (position.tokensOwed0 + uint128(amount0), position.tokensOwed1 + uint128(amount1));

655:                 state.protocolFee += uint128(delta);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

### <a name="L-11"></a>[L-11] Unspecific compiler version pragma

*Instances (1)*:

```solidity
File: contracts/libraries/PoolAddress.sol

2: pragma solidity >=0.5.0 <0.8.0;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/libraries/PoolAddress.sol)

### <a name="L-12"></a>[L-12] Upgradeable contract not initialized

Upgradeable contracts are initialized via an initializer function rather than by a constructor. Leaving such a contract uninitialized may lead to it being taken over by a malicious user

*Instances (22)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

15: import "contracts/base/PoolInitializer.sol";

29:     PoolInitializer,

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)

```solidity
File: contracts/ThrusterPool.sol

186:             bool initializedLower;

187:             (tickCumulativeLower, secondsPerLiquidityOutsideLowerX128, secondsOutsideLower, initializedLower) = (

191:                 lower.initialized

193:             require(initializedLower);

195:             bool initializedUpper;

196:             (tickCumulativeUpper, secondsPerLiquidityOutsideUpperX128, secondsOutsideUpper, initializedUpper) = (

200:                 upper.initialized

202:             require(initializedUpper);

269:     function initialize(uint160 sqrtPriceX96) external override {

274:         (uint16 cardinality, uint16 cardinalityNext) = observations.initialize(uint32(block.timestamp));

286:         emit Initialize(sqrtPriceX96, tick);

555:         bool initialized;

619:             (step.tickNext, step.initialized) =

620:                 tickBitmap.nextInitializedTickWithinOneWord(state.tick, tickSpacing, zeroForOne);

666:                 if (step.initialized) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/ThrusterPool.sol)

```solidity
File: contracts/base/PoolInitializer.sol

4: import "interfaces/IPoolInitializer.sol";

12: abstract contract PoolInitializer is IPoolInitializer, PeripheryImmutableState {

14:     function createAndInitializePoolIfNecessary(address token0, address token1, uint24 fee, uint160 sqrtPriceX96)

25:             IThrusterPool(pool).initialize(sqrtPriceX96);

29:                 IThrusterPool(pool).initialize(sqrtPriceX96);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/base/PoolInitializer.sol)

## Medium Issues

| |Issue|Instances|
|-|:-|:-:|
| [M-1](#M-1) | `_safeMint()` should be used rather than `_mint()` wherever possible | 1 |

### <a name="M-1"></a>[M-1] `_safeMint()` should be used rather than `_mint()` wherever possible

`_mint()` is [discouraged](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/d4d8d2ed9798cc3383912a23b5e8d5cb602f7d4b/contracts/token/ERC721/ERC721.sol#L271) in favor of `_safeMint()` which ensures that the recipient is either an EOA or implements `IERC721Receiver`. Both open [OpenZeppelin](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/d4d8d2ed9798cc3383912a23b5e8d5cb602f7d4b/contracts/token/ERC721/ERC721.sol#L238-L250) and [solmate](https://github.com/Rari-Capital/solmate/blob/4eaf6b68202e36f67cab379768ac6be304c8ebde/src/tokens/ERC721.sol#L180) have versions of this function so that NFTs aren't lost if they're minted to contracts that cannot transfer them back out.

Be careful however to respect the CEI pattern or add a re-entrancy guard as `_safeMint` adds a callback-check (`_checkOnERC721Received`) and a malicious `onERC721Received` could be exploited if not careful.

Reading material:

- <https://blocksecteam.medium.com/when-safemint-becomes-unsafe-lessons-from-the-hypebears-security-incident-2965209bda2a>
- <https://samczsun.com/the-dangers-of-surprising-code/>
- <https://github.com/KadenZipfel/smart-contract-attack-vectors/blob/master/vulnerabilities/unprotected-callback.md>

*Instances (1)*:

```solidity
File: contracts/NonfungiblePositionManager.sol

153:         _mint(params.recipient, (tokenId = _nextId++));

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-clmm/contracts/NonfungiblePositionManager.sol)
