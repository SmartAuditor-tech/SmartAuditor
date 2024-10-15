# Report

## Gas Optimizations

| |Issue|Instances|
|-|:-|:-:|
| [GAS-1](#GAS-1) | `a = a + b` is more gas effective than `a += b` for state variables (excluding arrays and mappings) | 2 |
| [GAS-2](#GAS-2) | Cache array length outside of loop | 2 |
| [GAS-3](#GAS-3) | State variables should be cached in stack variables rather than re-reading them from storage | 2 |
| [GAS-4](#GAS-4) | For Operations that will not overflow, you could use unchecked | 28 |
| [GAS-5](#GAS-5) | Use Custom Errors instead of Revert Strings to save Gas | 14 |
| [GAS-6](#GAS-6) | Avoid contract existence checks by using low level calls | 1 |
| [GAS-7](#GAS-7) | Stack variable used as a cheaper cache for a state variable is only used once | 1 |
| [GAS-8](#GAS-8) | State variables only set in the constructor should be declared `immutable` | 5 |
| [GAS-9](#GAS-9) | Functions guaranteed to revert when called by normal users can be marked `payable` | 5 |
| [GAS-10](#GAS-10) | `++i` costs less gas compared to `i++` or `i += 1` (same for `--i` vs `i--` or `i -= 1`) | 4 |
| [GAS-11](#GAS-11) | Using `private` rather than `public` for constants, saves gas | 1 |
| [GAS-12](#GAS-12) | Increments/decrements can be unchecked in for-loops | 4 |
| [GAS-13](#GAS-13) | Use != 0 instead of > 0 for unsigned integer comparison | 3 |
| [GAS-14](#GAS-14) | WETH address definition can be use directly | 1 |

### <a name="GAS-1"></a>[GAS-1] `a = a + b` is more gas effective than `a += b` for state variables (excluding arrays and mappings)

This saves **16 gas per instance.**

*Instances (2)*:

```solidity
File: contracts/ThrusterTreasure.sol

94:         currentTickets += ticketsToEnter;

255:         currentRound += 1;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-2"></a>[GAS-2] Cache array length outside of loop

If not cached, the solidity compiler will always read the length of the array during each iteration. That is, if it is a storage array, this is an extra sload operation (100 additional extra gas for each iteration except for the first) and if it is a memory array, this is an extra mload operation (3 additional gas for each iteration except for the first).

*Instances (2)*:

```solidity
File: contracts/ThrusterTreasure.sol

111:             for (uint256 j = 0; j < winningTicketsRoundPrize.length; j++) {

226:         for (uint256 i = 0; i < userCommitments.length; i++) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-3"></a>[GAS-3] State variables should be cached in stack variables rather than re-reading them from storage

The instances below point to the second+ access of a state variable within a function. Caching of a state variable replaces each Gwarmaccess (100 gas) with a much cheaper stack read. Other less obvious fixes/optimizations include having local memory caches of state variable structs, or having local caches of state variable contracts/addresses.

*Saves 100 gas per instance*

*Instances (2)*:

```solidity
File: contracts/ThrusterTreasure.sol

227:             uint64 sequenceNumber = entropy.request{value: fee}(entropyProvider, userCommitments[i], true);

239:         uint256 fee = entropy.getFee(entropyProvider);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-4"></a>[GAS-4] For Operations that will not overflow, you could use unchecked

*Instances (28)*:

```solidity
File: contracts/ThrusterTreasure.sol

4: import "@openzeppelin/contracts/access/Ownable.sol";

5: import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

6: import "@pythnetwork/entropy-sdk-solidity/IEntropy.sol";

8: import "interfaces/IERC20Rebasing.sol";

9: import "interfaces/IThrusterTreasure.sol";

10: import "interfaces/IBlast.sol";

18:         uint256 ticketStart; // Inclusive

19:         uint256 ticketEnd; // Not inclusive

31:     uint256 public constant MAX_ROUND_TIME = 30 days; // Time at most 30 days from when round is first initiated, not when winning tickets are drawn

41:     uint256 public currentRound; // Increments by 1 every time the root is updated

42:     uint256 public currentTickets; // Resets to 0 every time the root is updated

46:     mapping(address => mapping(uint256 => Round)) public entered; // Address => RoundIndex => Round

47:     mapping(uint256 => mapping(uint256 => Prize)) public prizes; // Need to keep track of prizes for each round. RoundIndex => PrizeIndex => Prize

48:     mapping(uint256 => mapping(uint256 => uint256[])) public winningTickets; // Need to keep track of winning tickets for each round. RoundIndex => PrizeIndex => WinningTickets

88:         uint256 ticketsToEnter = _amount - cumulativeTickets[msg.sender];

91:         Round memory round = Round(currentTickets_, currentTickets_ + ticketsToEnter, currentRound_);

93:         cumulativeTickets[msg.sender] = _amount; // Ensure user can only enter tickets once, no partials

94:         currentTickets += ticketsToEnter;

95:         emit EnteredTickets(msg.sender, currentTickets_, currentTickets_ + ticketsToEnter, currentRound_);

103:         require(roundStart[roundToClaim] + MAX_ROUND_TIME >= block.timestamp, "ICT");

108:         for (uint256 i = 0; i < maxPrizeCount_; i++) {

111:             for (uint256 j = 0; j < winningTicketsRoundPrize.length; j++) {

118:         entered[msg.sender][roundToClaim] = Round(0, 0, roundToClaim); // Clear user's tickets for the round

225:         require(address(this).balance >= fee * userCommitments.length, "IF");

226:         for (uint256 i = 0; i < userCommitments.length; i++) {

255:         currentRound += 1;

276:         require(roundStart[_round] + MAX_ROUND_TIME >= block.timestamp, "ICT");

286:         for (uint256 i = 0; i < numWinners; i++) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-5"></a>[GAS-5] Use Custom Errors instead of Revert Strings to save Gas

Custom errors are available from solidity version 0.8.4. Custom errors save [**~50 gas**](https://gist.github.com/IllIllI000/ad1bd0d29a0101b25e57c293b4b0c746) each time they're hit by [avoiding having to allocate and store the revert string](https://blog.soliditylang.org/2021/04/21/custom-errors/#errors-in-depth). Not defining the strings also save deployment gas

Additionally, custom errors can be used inside and outside of contracts (including interfaces and libraries).

Source: <https://blog.soliditylang.org/2021/04/21/custom-errors/>:

> Starting from [Solidity v0.8.4](https://github.com/ethereum/solidity/releases/tag/v0.8.4), there is a convenient and gas-efficient way to explain to users why an operation failed through the use of custom errors. Until now, you could already use strings to give more information about failures (e.g., `revert("Insufficient funds.");`), but they are rather expensive, especially when it comes to deploy cost, and it is difficult to use dynamic information in them.

Consider replacing **all revert strings** with custom errors in the solution, and particularly those that have multiple occurrences:

*Instances (14)*:

```solidity
File: contracts/ThrusterTreasure.sol

85:         require(winningTickets[currentRound_][0].length == 0, "ET");

87:         require(MerkleProof.verify(_proof, root, node), "IP");

89:         require(ticketsToEnter > 0, "NTE");

103:         require(roundStart[roundToClaim] + MAX_ROUND_TIME >= block.timestamp, "ICT");

104:         require(winningTickets[roundToClaim][0].length > 0, "NWT");

106:         require(round.ticketEnd > round.ticketStart, "NTE");

167:         require(_round >= currentRound, "ICR");

168:         require(_prizeIndex < maxPrizeCount, "IPC");

225:         require(address(this).balance >= fee * userCommitments.length, "IF");

240:         require(address(this).balance > fee, "IF");

276:         require(roundStart[_round] + MAX_ROUND_TIME >= block.timestamp, "ICT");

277:         require(winningTickets[_round][_prizeIndex].length == 0, "WTS");

291:         require(_winningTickets.length == numWinners, "WTL");

306:         require(currentTickets > 0, "NCT");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-6"></a>[GAS-6] Avoid contract existence checks by using low level calls

Prior to 0.8.10 the compiler inserted extra code, including `EXTCODESIZE` (**100 gas**), to check for contract existence for external function calls. In more recent solidity versions, the compiler will not insert these checks if the external call has a return value. Similar behavior can be achieved in earlier versions by using low-level calls, since low level calls never check for contract existence

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

195:             _amount = token.balanceOf(address(this));

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-7"></a>[GAS-7] Stack variable used as a cheaper cache for a state variable is only used once

If the variable is only accessed once, it's cheaper to use the state variable directly that one time, and save the **3 gas** the extra stack assignment would spend

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

107:         uint256 maxPrizeCount_ = maxPrizeCount;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-8"></a>[GAS-8] State variables only set in the constructor should be declared `immutable`

Variables only set in the constructor and never edited afterwards should be marked as immutable, as it would avoid the expensive storage-writing operation in the constructor (around **20 000 gas** per variable) and replace the expensive storage-reading operations (around **2100 gas** per reading) to a less expensive value reading (**3 gas**)

*Instances (5)*:

```solidity
File: contracts/ThrusterTreasure.sol

66:         entropy = IEntropy(_entropy);

67:         entropyProvider = _entropyProvider;

69:         BLAST = IBlast(_blast);

70:         WETH = IERC20Rebasing(_weth);

71:         USDB = IERC20Rebasing(_usdb);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-9"></a>[GAS-9] Functions guaranteed to revert when called by normal users can be marked `payable`

If a function modifier such as `onlyOwner` is used, the function will revert if a normal user tries to pay the function. Marking the function as `payable` will lower the gas cost for legitimate callers because the compiler will not include checks for whether a payment was provided.

*Instances (5)*:

```solidity
File: contracts/ThrusterTreasure.sol

139:     function setMaxPrizeCount(uint256 _maxPrizeCount) external onlyOwner {

150:     function claimYield(address _recipient, uint256 _amountWETH, uint256 _amountUSDB) external onlyOwner {

192:     function retrieveTokens(address _recipient, address _token, uint256 _amount) external onlyOwner {

253:     function setRoot(bytes32 _root) external onlyOwner {

321:     function claimGas(address _recipient, uint256 _minClaimRateBips) external onlyOwner returns (uint256 amount) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-10"></a>[GAS-10] `++i` costs less gas compared to `i++` or `i += 1` (same for `--i` vs `i--` or `i -= 1`)

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

*Instances (4)*:

```solidity
File: contracts/ThrusterTreasure.sol

108:         for (uint256 i = 0; i < maxPrizeCount_; i++) {

111:             for (uint256 j = 0; j < winningTicketsRoundPrize.length; j++) {

226:         for (uint256 i = 0; i < userCommitments.length; i++) {

286:         for (uint256 i = 0; i < numWinners; i++) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-11"></a>[GAS-11] Using `private` rather than `public` for constants, saves gas

If needed, the values can be read from the verified contract source code, or if there are multiple values there can be a single getter function that [returns a tuple](https://github.com/code-423n4/2022-08-frax/blob/90f55a9ce4e25bceed3a74290b854341d8de6afa/src/contracts/FraxlendPair.sol#L156-L178) of the values of all currently-public constants. Saves **3406-3606 gas** in deployment gas due to the compiler not having to create non-payable getter functions for deployment calldata, not having to store the bytes of the value outside of where it's used, and not adding another entry to the method ID table

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

31:     uint256 public constant MAX_ROUND_TIME = 30 days; // Time at most 30 days from when round is first initiated, not when winning tickets are drawn

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-12"></a>[GAS-12] Increments/decrements can be unchecked in for-loops

In Solidity 0.8+, there's a default overflow check on unsigned integers. It's possible to uncheck this in for-loops and save some gas at each iteration, but at the cost of some code readability, as this uncheck cannot be made inline.

[ethereum/solidity#10695](https://github.com/ethereum/solidity/issues/10695)

The change would be:

```diff
- for (uint256 i; i < numIterations; i++) {
+ for (uint256 i; i < numIterations;) {
 // ...  
+   unchecked { ++i; }
}  
```

These save around **25 gas saved** per instance.

The same can be applied with decrements (which should use `break` when `i == 0`).

The risk of overflow is non-existent for `uint256`.

*Instances (4)*:

```solidity
File: contracts/ThrusterTreasure.sol

108:         for (uint256 i = 0; i < maxPrizeCount_; i++) {

111:             for (uint256 j = 0; j < winningTicketsRoundPrize.length; j++) {

226:         for (uint256 i = 0; i < userCommitments.length; i++) {

286:         for (uint256 i = 0; i < numWinners; i++) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-13"></a>[GAS-13] Use != 0 instead of > 0 for unsigned integer comparison

*Instances (3)*:

```solidity
File: contracts/ThrusterTreasure.sol

89:         require(ticketsToEnter > 0, "NTE");

104:         require(winningTickets[roundToClaim][0].length > 0, "NWT");

306:         require(currentTickets > 0, "NCT");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="GAS-14"></a>[GAS-14] WETH address definition can be use directly

WETH is a wrap Ether contract with a specific address in the Ethereum network, giving the option to define it may cause false recognition, it is healthier to define it directly.

    Advantages of defining a specific contract directly:
    
    It saves gas,
    Prevents incorrect argument definition,
    Prevents execution on a different chain and re-signature issues,
    WETH Address : 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

34:     IERC20Rebasing public immutable WETH;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

## Non Critical Issues

| |Issue|Instances|
|-|:-|:-:|
| [NC-1](#NC-1) | Missing checks for `address(0)` when assigning values to address state variables | 1 |
| [NC-2](#NC-2) | Array indices should be referenced via `enum`s rather than via numeric literals | 2 |
| [NC-3](#NC-3) | Use `string.concat()` or `bytes.concat()` instead of `abi.encodePacked` | 1 |
| [NC-4](#NC-4) | Control structures do not follow the Solidity Style Guide | 3 |
| [NC-5](#NC-5) | Consider disabling `renounceOwnership()` | 1 |
| [NC-6](#NC-6) | Duplicated `require()`/`revert()` Checks Should Be Refactored To A Modifier Or Function | 6 |
| [NC-7](#NC-7) | Events that mark critical parameter changes should contain both the old and the new value | 3 |
| [NC-8](#NC-8) | Function ordering does not follow the Solidity style guide | 1 |
| [NC-9](#NC-9) | Functions should not be longer than 50 lines | 14 |
| [NC-10](#NC-10) | Lack of checks in setters | 2 |
| [NC-11](#NC-11) | Lines are too long | 1 |
| [NC-12](#NC-12) | Missing Event for critical parameters change | 1 |
| [NC-13](#NC-13) | Incomplete NatSpec: `@return` is missing on actually documented functions | 4 |
| [NC-14](#NC-14) | Consider using named mappings | 6 |
| [NC-15](#NC-15) | Contract does not follow the Solidity style guide's suggested layout ordering | 1 |
| [NC-16](#NC-16) | Some require descriptions are not clear | 14 |
| [NC-17](#NC-17) | Internal and private variables and functions names should begin with an underscore | 4 |
| [NC-18](#NC-18) | Usage of floating `pragma` is not recommended | 1 |
| [NC-19](#NC-19) | Variables need not be initialized to zero | 4 |

### <a name="NC-1"></a>[NC-1] Missing checks for `address(0)` when assigning values to address state variables

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

67:         entropyProvider = _entropyProvider;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-2"></a>[NC-2] Array indices should be referenced via `enum`s rather than via numeric literals

*Instances (2)*:

```solidity
File: contracts/ThrusterTreasure.sol

85:         require(winningTickets[currentRound_][0].length == 0, "ET");

104:         require(winningTickets[roundToClaim][0].length > 0, "NWT");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-3"></a>[NC-3] Use `string.concat()` or `bytes.concat()` instead of `abi.encodePacked`

Solidity version 0.8.4 introduces `bytes.concat()` (vs `abi.encodePacked(<bytes>,<bytes>)`)

Solidity version 0.8.12 introduces `string.concat()` (vs `abi.encodePacked(<str>,<str>), which catches concatenation errors (in the event of a`bytes`data mixed in the concatenation)`)

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

86:         bytes32 node = keccak256(abi.encodePacked(msg.sender, _amount));

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-4"></a>[NC-4] Control structures do not follow the Solidity Style Guide

See the [control structures](https://docs.soliditylang.org/en/latest/style-guide.html#control-structures) section of the Solidity Style Guide

*Instances (3)*:

```solidity
File: contracts/ThrusterTreasure.sol

87:         require(MerkleProof.verify(_proof, root, node), "IP");

225:         require(address(this).balance >= fee * userCommitments.length, "IF");

240:         require(address(this).balance > fee, "IF");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-5"></a>[NC-5] Consider disabling `renounceOwnership()`

If the plan for your project does not include eventually giving up all ownership control, consider overwriting OpenZeppelin's `Ownable`'s `renounceOwnership()` function in order to disable it.

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

16: contract ThrusterTreasure is Ownable, IThrusterTreasure {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-6"></a>[NC-6] Duplicated `require()`/`revert()` Checks Should Be Refactored To A Modifier Or Function

*Instances (6)*:

```solidity
File: contracts/ThrusterTreasure.sol

89:         require(ticketsToEnter > 0, "NTE");

103:         require(roundStart[roundToClaim] + MAX_ROUND_TIME >= block.timestamp, "ICT");

106:         require(round.ticketEnd > round.ticketStart, "NTE");

225:         require(address(this).balance >= fee * userCommitments.length, "IF");

240:         require(address(this).balance > fee, "IF");

276:         require(roundStart[_round] + MAX_ROUND_TIME >= block.timestamp, "ICT");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-7"></a>[NC-7] Events that mark critical parameter changes should contain both the old and the new value

This should especially be done if the new value is not required to be different from the old value

*Instances (3)*:

```solidity
File: contracts/ThrusterTreasure.sol

139:     function setMaxPrizeCount(uint256 _maxPrizeCount) external onlyOwner {
             maxPrizeCount = _maxPrizeCount;
             emit SetMaxPrizeCount(_maxPrizeCount);

253:     function setRoot(bytes32 _root) external onlyOwner {
             root = _root;
             currentRound += 1;
             roundStart[currentRound] = block.timestamp;
             currentTickets = 0;
             emit NewRound(_root, currentRound);

269:     function setWinningTickets(
             uint256 _round,
             uint256 _prizeIndex,
             uint64[] calldata sequenceNumbers,
             bytes32[] calldata userRandoms,
             bytes32[] calldata providerRandoms
         ) external onlyOwner {
             require(roundStart[_round] + MAX_ROUND_TIME >= block.timestamp, "ICT");
             require(winningTickets[_round][_prizeIndex].length == 0, "WTS");
             Prize memory prize_ = prizes[_round][_prizeIndex];
             uint256 numWinners = prize_.numWinners;
             require(
                 sequenceNumbers.length == numWinners && userRandoms.length == numWinners
                     && providerRandoms.length == numWinners,
                 "WL"
             );
             uint256[] memory _winningTickets = new uint256[](numWinners);
             for (uint256 i = 0; i < numWinners; i++) {
                 _winningTickets[i] = revealRandomNumber(sequenceNumbers[i], userRandoms[i], providerRandoms[i]);
                 emit SetWinningTicket(_round, _prizeIndex, _winningTickets[i], i);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-8"></a>[NC-8] Function ordering does not follow the Solidity style guide

According to the [Solidity style guide](https://docs.soliditylang.org/en/v0.8.17/style-guide.html#order-of-functions), functions should be laid out in the following order :`constructor()`, `receive()`, `fallback()`, `external`, `public`, `internal`, `private`, but the cases below do not follow this pattern

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

1: 
   Current order:
   external enterTickets
   external claimPrizesForRound
   internal _claimPrize
   external setMaxPrizeCount
   external claimYield
   external setPrize
   internal depositPrize
   external retrieveTokens
   external retrieveETH
   external requestRandomNumberMany
   external requestRandomNumber
   external setRoot
   external setWinningTickets
   public revealRandomNumber
   external claimGas
   
   Suggested order:
   external enterTickets
   external claimPrizesForRound
   external setMaxPrizeCount
   external claimYield
   external setPrize
   external retrieveTokens
   external retrieveETH
   external requestRandomNumberMany
   external requestRandomNumber
   external setRoot
   external setWinningTickets
   external claimGas
   public revealRandomNumber
   internal _claimPrize
   internal depositPrize

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-9"></a>[NC-9] Functions should not be longer than 50 lines

Overly complex code can make understanding functionality more difficult, try to further modularize your code to ensure readability

*Instances (14)*:

```solidity
File: contracts/ThrusterTreasure.sol

83:     function enterTickets(uint256 _amount, bytes32[] calldata _proof) external {

102:     function claimPrizesForRound(uint256 roundToClaim) external {

127:     function _claimPrize(Prize memory _prize, address _receiver, uint256 _winningTicket) internal {

139:     function setMaxPrizeCount(uint256 _maxPrizeCount) external onlyOwner {

150:     function claimYield(address _recipient, uint256 _amountWETH, uint256 _amountUSDB) external onlyOwner {

163:     function setPrize(uint256 _round, uint64 _prizeIndex, uint256 _amountWETH, uint256 _amountUSDB, uint64 _numWinners)

180:     function depositPrize(address _from, uint256 _amountWETH, uint256 _amountUSDB) internal {

192:     function retrieveTokens(address _recipient, address _token, uint256 _amount) external onlyOwner {

206:     function retrieveETH(address payable _recipient, uint256 _amount) external onlyOwner {

218:     function requestRandomNumberMany(bytes32[] calldata userCommitments)

238:     function requestRandomNumber(bytes32 userCommitment) external payable onlyOwner returns (uint64) {

253:     function setRoot(bytes32 _root) external onlyOwner {

301:     function revealRandomNumber(uint64 sequenceNumber, bytes32 userRandom, bytes32 providerRandom)

321:     function claimGas(address _recipient, uint256 _minClaimRateBips) external onlyOwner returns (uint256 amount) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-10"></a>[NC-10] Lack of checks in setters

Be it sanity checks (like checks against `0`-values) or initial setting checks: it's best for Setter functions to have them

*Instances (2)*:

```solidity
File: contracts/ThrusterTreasure.sol

139:     function setMaxPrizeCount(uint256 _maxPrizeCount) external onlyOwner {
             maxPrizeCount = _maxPrizeCount;
             emit SetMaxPrizeCount(_maxPrizeCount);

253:     function setRoot(bytes32 _root) external onlyOwner {
             root = _root;
             currentRound += 1;
             roundStart[currentRound] = block.timestamp;
             currentTickets = 0;
             emit NewRound(_root, currentRound);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-11"></a>[NC-11] Lines are too long

Usually lines in source code are limited to [80](https://softwareengineering.stackexchange.com/questions/148677/why-is-80-characters-the-standard-limit-for-code-width) characters. Today's screens are much larger so it's reasonable to stretch this in some cases. Since the files will most likely reside in GitHub, and GitHub starts using a scroll bar in all cases when the length is over [164](https://github.com/aizatto/character-length) characters, the lines below should be split when they reach that length

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

48:     mapping(uint256 => mapping(uint256 => uint256[])) public winningTickets; // Need to keep track of winning tickets for each round. RoundIndex => PrizeIndex => WinningTickets

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-12"></a>[NC-12] Missing Event for critical parameters change

Events help non-contract tools to track changes, and events prevent users from being surprised by changes.

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

163:     function setPrize(uint256 _round, uint64 _prizeIndex, uint256 _amountWETH, uint256 _amountUSDB, uint64 _numWinners)
             external
             onlyOwner
         {
             require(_round >= currentRound, "ICR");
             require(_prizeIndex < maxPrizeCount, "IPC");
             depositPrize(msg.sender, _amountWETH, _amountUSDB);
             prizes[_round][_prizeIndex] = Prize(_amountWETH, _amountUSDB, _numWinners, _prizeIndex, uint64(_round));

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-13"></a>[NC-13] Incomplete NatSpec: `@return` is missing on actually documented functions

The following functions are missing `@return` NatSpec comments.

*Instances (4)*:

```solidity
File: contracts/ThrusterTreasure.sol

214:     /**
          * Request many random numbers using Pyth Entropy
          * @param userCommitments - The user's commitments
          */
         function requestRandomNumberMany(bytes32[] calldata userCommitments)
             external
             payable
             onlyOwner
             returns (uint64[] memory seqNums)

234:     /**
          * Request a random number using Pyth Entropy
          * @param userCommitment - The user's commitment
          */
         function requestRandomNumber(bytes32 userCommitment) external payable onlyOwner returns (uint64) {

294:     /**
          * Reveals the random number using Pyth Entropy.
          *
          * @param sequenceNumber - The sequence number of the random number request
          * @param userRandom - The user's random number
          * @param providerRandom - The provider's random number
          */
         function revealRandomNumber(uint64 sequenceNumber, bytes32 userRandom, bytes32 providerRandom)
             public
             onlyOwner
             returns (uint256)

316:     /**
          * Claims the gas from the BLAST contract
          * @param _recipient - The address to claim the yield to
          * @param _minClaimRateBips - The minimum claim rate in bips
          */
         function claimGas(address _recipient, uint256 _minClaimRateBips) external onlyOwner returns (uint256 amount) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-14"></a>[NC-14] Consider using named mappings

Consider moving to solidity version 0.8.18 or later, and using [named mappings](https://ethereum.stackexchange.com/questions/51629/how-to-name-the-arguments-in-mapping/145555#145555) to make it easier to understand the purpose of each mapping

*Instances (6)*:

```solidity
File: contracts/ThrusterTreasure.sol

44:     mapping(uint256 => uint256) public roundStart;

45:     mapping(address => uint256) public cumulativeTickets;

46:     mapping(address => mapping(uint256 => Round)) public entered; // Address => RoundIndex => Round

47:     mapping(uint256 => mapping(uint256 => Prize)) public prizes; // Need to keep track of prizes for each round. RoundIndex => PrizeIndex => Prize

48:     mapping(uint256 => mapping(uint256 => uint256[])) public winningTickets; // Need to keep track of winning tickets for each round. RoundIndex => PrizeIndex => WinningTickets

49:     mapping(uint64 => address) private requestedRandomNumber;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-15"></a>[NC-15] Contract does not follow the Solidity style guide's suggested layout ordering

The [style guide](https://docs.soliditylang.org/en/v0.8.16/style-guide.html#order-of-layout) says that, within a contract, the ordering should be:

1) Type declarations
2) State variables
3) Events
4) Modifiers
5) Functions

However, the contract(s) below do not follow this ordering

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

1: 
   Current order:
   StructDefinition.Round
   StructDefinition.Prize
   VariableDeclaration.MAX_ROUND_TIME
   VariableDeclaration.BLAST
   VariableDeclaration.WETH
   VariableDeclaration.USDB
   VariableDeclaration.entropy
   VariableDeclaration.entropyProvider
   VariableDeclaration.root
   VariableDeclaration.currentRound
   VariableDeclaration.currentTickets
   VariableDeclaration.maxPrizeCount
   VariableDeclaration.roundStart
   VariableDeclaration.cumulativeTickets
   VariableDeclaration.entered
   VariableDeclaration.prizes
   VariableDeclaration.winningTickets
   VariableDeclaration.requestedRandomNumber
   FunctionDefinition.constructor
   FunctionDefinition.enterTickets
   FunctionDefinition.claimPrizesForRound
   FunctionDefinition._claimPrize
   FunctionDefinition.setMaxPrizeCount
   FunctionDefinition.claimYield
   FunctionDefinition.setPrize
   FunctionDefinition.depositPrize
   FunctionDefinition.retrieveTokens
   FunctionDefinition.retrieveETH
   FunctionDefinition.requestRandomNumberMany
   FunctionDefinition.requestRandomNumber
   FunctionDefinition.setRoot
   FunctionDefinition.setWinningTickets
   FunctionDefinition.revealRandomNumber
   FunctionDefinition.claimGas
   FunctionDefinition.receive
   
   Suggested order:
   VariableDeclaration.MAX_ROUND_TIME
   VariableDeclaration.BLAST
   VariableDeclaration.WETH
   VariableDeclaration.USDB
   VariableDeclaration.entropy
   VariableDeclaration.entropyProvider
   VariableDeclaration.root
   VariableDeclaration.currentRound
   VariableDeclaration.currentTickets
   VariableDeclaration.maxPrizeCount
   VariableDeclaration.roundStart
   VariableDeclaration.cumulativeTickets
   VariableDeclaration.entered
   VariableDeclaration.prizes
   VariableDeclaration.winningTickets
   VariableDeclaration.requestedRandomNumber
   StructDefinition.Round
   StructDefinition.Prize
   FunctionDefinition.constructor
   FunctionDefinition.enterTickets
   FunctionDefinition.claimPrizesForRound
   FunctionDefinition._claimPrize
   FunctionDefinition.setMaxPrizeCount
   FunctionDefinition.claimYield
   FunctionDefinition.setPrize
   FunctionDefinition.depositPrize
   FunctionDefinition.retrieveTokens
   FunctionDefinition.retrieveETH
   FunctionDefinition.requestRandomNumberMany
   FunctionDefinition.requestRandomNumber
   FunctionDefinition.setRoot
   FunctionDefinition.setWinningTickets
   FunctionDefinition.revealRandomNumber
   FunctionDefinition.claimGas
   FunctionDefinition.receive

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-16"></a>[NC-16] Some require descriptions are not clear

1. It does not comply with the general require error description model of the project (Either all of them should be debugged in this way, or all of them should be explained with a string not exceeding 32 bytes.)
2. For debug dapps like Tenderly, these debug messages are important, this allows the user to see the reasons for revert practically.

*Instances (14)*:

```solidity
File: contracts/ThrusterTreasure.sol

85:         require(winningTickets[currentRound_][0].length == 0, "ET");

87:         require(MerkleProof.verify(_proof, root, node), "IP");

89:         require(ticketsToEnter > 0, "NTE");

103:         require(roundStart[roundToClaim] + MAX_ROUND_TIME >= block.timestamp, "ICT");

104:         require(winningTickets[roundToClaim][0].length > 0, "NWT");

106:         require(round.ticketEnd > round.ticketStart, "NTE");

167:         require(_round >= currentRound, "ICR");

168:         require(_prizeIndex < maxPrizeCount, "IPC");

225:         require(address(this).balance >= fee * userCommitments.length, "IF");

240:         require(address(this).balance > fee, "IF");

276:         require(roundStart[_round] + MAX_ROUND_TIME >= block.timestamp, "ICT");

277:         require(winningTickets[_round][_prizeIndex].length == 0, "WTS");

291:         require(_winningTickets.length == numWinners, "WTL");

306:         require(currentTickets > 0, "NCT");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-17"></a>[NC-17] Internal and private variables and functions names should begin with an underscore

According to the Solidity Style Guide, Non-`external` variable and function names should begin with an [underscore](https://docs.soliditylang.org/en/latest/style-guide.html#underscore-prefix-for-non-external-functions-and-variables)

*Instances (4)*:

```solidity
File: contracts/ThrusterTreasure.sol

37:     IEntropy private entropy;

38:     address private entropyProvider;

49:     mapping(uint64 => address) private requestedRandomNumber;

180:     function depositPrize(address _from, uint256 _amountWETH, uint256 _amountUSDB) internal {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-18"></a>[NC-18] Usage of floating `pragma` is not recommended

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

2: pragma solidity ^0.8.23;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="NC-19"></a>[NC-19] Variables need not be initialized to zero

The default value for variables is zero, so initializing them to zero is superfluous.

*Instances (4)*:

```solidity
File: contracts/ThrusterTreasure.sol

108:         for (uint256 i = 0; i < maxPrizeCount_; i++) {

111:             for (uint256 j = 0; j < winningTicketsRoundPrize.length; j++) {

226:         for (uint256 i = 0; i < userCommitments.length; i++) {

286:         for (uint256 i = 0; i < numWinners; i++) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

## Low Issues

| |Issue|Instances|
|-|:-|:-:|
| [L-1](#L-1) | Use a 2-step ownership transfer pattern | 1 |
| [L-2](#L-2) | Some tokens may revert when zero value transfers are made | 5 |
| [L-3](#L-3) | Missing checks for `address(0)` when assigning values to address state variables | 1 |
| [L-4](#L-4) | Empty `receive()/payable fallback()` function does not authenticate requests | 1 |
| [L-5](#L-5) | Signature use at deadlines should be allowed | 2 |
| [L-6](#L-6) | Solidity version 0.8.20+ may not work on other chains due to `PUSH0` | 1 |
| [L-7](#L-7) | Use `Ownable2Step.transferOwnership` instead of `Ownable.transferOwnership` | 1 |
| [L-8](#L-8) | Consider using OpenZeppelin's SafeCast library to prevent unexpected overflows when downcasting | 1 |
| [L-9](#L-9) | Unsafe ERC20 operation(s) | 6 |

### <a name="L-1"></a>[L-1] Use a 2-step ownership transfer pattern

Recommend considering implementing a two step process where the owner or admin nominates an account and the nominated account needs to call an `acceptOwnership()` function for the transfer of ownership to fully succeed. This ensures the nominated EOA account is a valid and active account. Lack of two-step procedure for critical operations leaves them error-prone. Consider adding two step procedure on the critical functions.

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

16: contract ThrusterTreasure is Ownable, IThrusterTreasure {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="L-2"></a>[L-2] Some tokens may revert when zero value transfers are made

Example: <https://github.com/d-xo/weird-erc20#revert-on-zero-value-transfers>.

In spite of the fact that EIP-20 [states](https://github.com/ethereum/EIPs/blob/46b9b698815abbfa628cd1097311deee77dd45c5/EIPS/eip-20.md?plain=1#L116) that zero-valued transfers must be accepted, some tokens, such as LEND will revert if this is attempted, which may cause transactions that involve other tokens (such as batch operations) to fully revert. Consider skipping the transfer if the amount is zero, which will also save gas.

*Instances (5)*:

```solidity
File: contracts/ThrusterTreasure.sol

130:         WETH.transfer(_receiver, amountETH);

131:         USDB.transfer(_receiver, amountUSDB);

181:         WETH.transferFrom(_from, address(this), _amountWETH);

182:         USDB.transferFrom(_from, address(this), _amountUSDB);

197:         token.transfer(_recipient, _amount);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="L-3"></a>[L-3] Missing checks for `address(0)` when assigning values to address state variables

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

67:         entropyProvider = _entropyProvider;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="L-4"></a>[L-4] Empty `receive()/payable fallback()` function does not authenticate requests

If the intention is for the Ether to be used, the function should call another function, otherwise it should revert (e.g. require(msg.sender == address(weth))). Having no access control on the function means that someone may send Ether to the contract, and have no way to get anything back out, which is a loss of funds. If the concern is having to spend a small amount of gas to check the sender against an immutable address, the code should at least have a function to rescue unused Ether.

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

330:     receive() external payable {}

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="L-5"></a>[L-5] Signature use at deadlines should be allowed

According to [EIP-2612](https://github.com/ethereum/EIPs/blob/71dc97318013bf2ac572ab63fab530ac9ef419ca/EIPS/eip-2612.md?plain=1#L58), signatures used on exactly the deadline timestamp are supposed to be allowed. While the signature may or may not be used for the exact EIP-2612 use case (transfer approvals), for consistency's sake, all deadlines should follow this semantic. If the timestamp is an expiration rather than a deadline, consider whether it makes more sense to include the expiration timestamp as a valid timestamp, as is done for deadlines.

*Instances (2)*:

```solidity
File: contracts/ThrusterTreasure.sol

103:         require(roundStart[roundToClaim] + MAX_ROUND_TIME >= block.timestamp, "ICT");

276:         require(roundStart[_round] + MAX_ROUND_TIME >= block.timestamp, "ICT");

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="L-6"></a>[L-6] Solidity version 0.8.20+ may not work on other chains due to `PUSH0`

The compiler for Solidity 0.8.20 switches the default target EVM version to [Shanghai](https://blog.soliditylang.org/2023/05/10/solidity-0.8.20-release-announcement/#important-note), which includes the new `PUSH0` op code. This op code may not yet be implemented on all L2s, so deployment on these chains will fail. To work around this issue, use an earlier [EVM](https://docs.soliditylang.org/en/v0.8.20/using-the-compiler.html?ref=zaryabs.com#setting-the-evm-version-to-target) [version](https://book.getfoundry.sh/reference/config/solidity-compiler#evm_version). While the project itself may or may not compile with 0.8.20, other projects with which it integrates, or which extend this project may, and those projects will have problems deploying these contracts/libraries.

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

2: pragma solidity ^0.8.23;

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="L-7"></a>[L-7] Use `Ownable2Step.transferOwnership` instead of `Ownable.transferOwnership`

Use [Ownable2Step.transferOwnership](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable2Step.sol) which is safer. Use it as it is more secure due to 2-stage ownership transfer.

**Recommended Mitigation Steps**

Use <a href="https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable2Step.sol">Ownable2Step.sol</a>
  
  ```solidity
      function acceptOwnership() external {
          address sender = _msgSender();
          require(pendingOwner() == sender, "Ownable2Step: caller is not the new owner");
          _transferOwnership(sender);
      }
```

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

4: import "@openzeppelin/contracts/access/Ownable.sol";

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="L-8"></a>[L-8] Consider using OpenZeppelin's SafeCast library to prevent unexpected overflows when downcasting

Downcasting from `uint256`/`int256` in Solidity does not revert on overflow. This can result in undesired exploitation or bugs, since developers usually assume that overflows raise errors. [OpenZeppelin's SafeCast library](https://docs.openzeppelin.com/contracts/3.x/api/utils#SafeCast) restores this intuition by reverting the transaction when such an operation overflows. Using this library eliminates an entire class of bugs, so it's recommended to use it always. Some exceptions are acceptable like with the classic `uint256(uint160(address(variable)))`

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

170:         prizes[_round][_prizeIndex] = Prize(_amountWETH, _amountUSDB, _numWinners, _prizeIndex, uint64(_round));

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="L-9"></a>[L-9] Unsafe ERC20 operation(s)

*Instances (6)*:

```solidity
File: contracts/ThrusterTreasure.sol

130:         WETH.transfer(_receiver, amountETH);

131:         USDB.transfer(_receiver, amountUSDB);

181:         WETH.transferFrom(_from, address(this), _amountWETH);

182:         USDB.transferFrom(_from, address(this), _amountUSDB);

197:         token.transfer(_recipient, _amount);

210:         _recipient.transfer(_amount);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

## Medium Issues

| |Issue|Instances|
|-|:-|:-:|
| [M-1](#M-1) | Contracts are vulnerable to fee-on-transfer accounting-related issues | 2 |
| [M-2](#M-2) | Centralization Risk for trusted owners | 10 |
| [M-3](#M-3) | `call()` should be used instead of `transfer()` on an `address payable` | 1 |
| [M-4](#M-4) | Return values of `transfer()`/`transferFrom()` not checked | 5 |
| [M-5](#M-5) | Unsafe use of `transfer()`/`transferFrom()` with `IERC20` | 5 |

### <a name="M-1"></a>[M-1] Contracts are vulnerable to fee-on-transfer accounting-related issues

Consistently check account balance before and after transfers for Fee-On-Transfer discrepancies. As arbitrary ERC20 tokens can be used, the amount here should be calculated every time to take into consideration a possible fee-on-transfer or deflation.
Also, it's a good practice for the future of the solution.

Use the balance before and after the transfer to calculate the received amount instead of assuming that it would be equal to the amount passed as a parameter. Or explicitly document that such tokens shouldn't be used and won't be supported

*Instances (2)*:

```solidity
File: contracts/ThrusterTreasure.sol

181:         WETH.transferFrom(_from, address(this), _amountWETH);

182:         USDB.transferFrom(_from, address(this), _amountUSDB);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="M-2"></a>[M-2] Centralization Risk for trusted owners

#### Impact

Contracts have owners with privileged rights to perform admin tasks and need to be trusted to not perform malicious updates or drain funds.

*Instances (10)*:

```solidity
File: contracts/ThrusterTreasure.sol

16: contract ThrusterTreasure is Ownable, IThrusterTreasure {

65:     ) Ownable(msg.sender) {

139:     function setMaxPrizeCount(uint256 _maxPrizeCount) external onlyOwner {

150:     function claimYield(address _recipient, uint256 _amountWETH, uint256 _amountUSDB) external onlyOwner {

192:     function retrieveTokens(address _recipient, address _token, uint256 _amount) external onlyOwner {

206:     function retrieveETH(address payable _recipient, uint256 _amount) external onlyOwner {

238:     function requestRandomNumber(bytes32 userCommitment) external payable onlyOwner returns (uint64) {

253:     function setRoot(bytes32 _root) external onlyOwner {

275:     ) external onlyOwner {

321:     function claimGas(address _recipient, uint256 _minClaimRateBips) external onlyOwner returns (uint256 amount) {

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="M-3"></a>[M-3] `call()` should be used instead of `transfer()` on an `address payable`

The use of the deprecated `transfer()` function for an address may make the transaction fail due to the 2300 gas stipend

*Instances (1)*:

```solidity
File: contracts/ThrusterTreasure.sol

210:         _recipient.transfer(_amount);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="M-4"></a>[M-4] Return values of `transfer()`/`transferFrom()` not checked

Not all `IERC20` implementations `revert()` when there's a failure in `transfer()`/`transferFrom()`. The function signature has a `boolean` return value and they indicate errors that way instead. By not checking the return value, operations that should have marked as failed, may potentially go through without actually making a payment

*Instances (5)*:

```solidity
File: contracts/ThrusterTreasure.sol

130:         WETH.transfer(_receiver, amountETH);

131:         USDB.transfer(_receiver, amountUSDB);

181:         WETH.transferFrom(_from, address(this), _amountWETH);

182:         USDB.transferFrom(_from, address(this), _amountUSDB);

197:         token.transfer(_recipient, _amount);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)

### <a name="M-5"></a>[M-5] Unsafe use of `transfer()`/`transferFrom()` with `IERC20`

Some tokens do not implement the ERC20 standard properly but are still accepted by most code that accepts ERC20 tokens.  For example Tether (USDT)'s `transfer()` and `transferFrom()` functions on L1 do not return booleans as the specification requires, and instead have no return value. When these sorts of tokens are cast to `IERC20`, their [function signatures](https://medium.com/coinmonks/missing-return-value-bug-at-least-130-tokens-affected-d67bf08521ca) do not match and therefore the calls made, revert (see [this](https://gist.github.com/IllIllI000/2b00a32e8f0559e8f386ea4f1800abc5) link for a test case). Use OpenZeppelin's `SafeERC20`'s `safeTransfer()`/`safeTransferFrom()` instead

*Instances (5)*:

```solidity
File: contracts/ThrusterTreasure.sol

130:         WETH.transfer(_receiver, amountETH);

131:         USDB.transfer(_receiver, amountUSDB);

181:         WETH.transferFrom(_from, address(this), _amountWETH);

182:         USDB.transferFrom(_from, address(this), _amountUSDB);

197:         token.transfer(_recipient, _amount);

```

[Link to code](https://github.com/code-423n4/2024-02-thruster/blob/main/thruster-protocol/thruster-treasure/contracts/ThrusterTreasure.sol)
