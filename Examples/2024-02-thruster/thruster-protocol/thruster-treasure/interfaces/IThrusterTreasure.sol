// SPDX-License-Identifier: BUSL-1.1
pragma solidity >=0.8.20;

interface IThrusterTreasure {
    event CheckedPrizesForRound(address user, uint256 round);
    event ClaimGas(address indexed recipient, uint256 amount);
    event ClaimedPrize(
        address user, uint256 round, uint256 prizeIndex, uint256 amountWETH, uint256 amountUSDB, uint256 winningTicket
    );
    event DepositedPrizes(uint256 amountWETH, uint256 amountUSDB);
    event EnteredTickets(address user, uint256 ticketRangeStart, uint256 ticketRangeEnd, uint256 currentRound);
    event NewRound(bytes32 root, uint256 round);
    event RandomNumberRequest(uint64 sequenceNumber, bytes32 userCommitment);
    event RandomNumberResult(uint256 randomNumber, uint64 sequenceNumber);
    event SetMaxPrizeCount(uint256 maxPrizeCount);
    event SetWinningTicket(uint256 round, uint256 prizeIndex, uint256 winningTicket, uint256 count);
    event WithdrawPrizes(address recipient, address token, uint256 amount);

    function setRoot(bytes32 root) external;

    function enterTickets(uint256 amount, bytes32[] calldata proof) external;

    function claimPrizesForRound(uint256 roundToClaim) external;

    function setMaxPrizeCount(uint256 maxPrizeCount) external;

    function setPrize(uint256 _round, uint64 _prizeIndex, uint256 _amountWETH, uint256 _amountUSDB, uint64 _numWinners)
        external;

    function claimYield(address _recipient, uint256 _amountWETH, uint256 _amountUSDB) external;


    function retrieveTokens(address recipient, address token, uint256 amount) external;

    function retrieveETH(address payable recipient, uint256 amount) external;

    function requestRandomNumberMany(bytes32[] calldata userCommitments) external payable returns (uint64[] memory seqNums);

    function requestRandomNumber(bytes32 userCommitment) external payable returns (uint64);

    function setWinningTickets(
        uint256 _round,
        uint256 _prizeIndex,
        uint64[] calldata sequenceNumbers,
        bytes32[] calldata userRandoms,
        bytes32[] calldata providerRandoms
    ) external;

    function revealRandomNumber(uint64 sequenceNumber, bytes32 userRandom, bytes32 providerRandom)
        external
        returns (uint256);
}
