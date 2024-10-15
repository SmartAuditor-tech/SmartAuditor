// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.23;

import "../lib/openzeppelin-contracts/contracts/access/Ownable.sol";
import "../lib/openzeppelin-contracts/contracts/utils/cryptography/MerkleProof.sol";
import "../interfaces/IEntropy.sol";

import "../interfaces/IERC20Rebasing.sol";
import "../interfaces/IThrusterTreasure.sol";
import "../interfaces/IBlast.sol";

/**
 * @title ThrusterTreasure
 * @notice Contract for Thruster Treasure, a lottery game that uses entropy to determine winners
 */
contract ThrusterTreasure is Ownable, IThrusterTreasure {
    struct Round {
        uint256 ticketStart; // Inclusive
        uint256 ticketEnd; // Not inclusive
        uint256 round;
    }

    struct Prize {
        uint256 amountWETH;
        uint256 amountUSDB;
        uint64 numWinners;
        uint64 prizeIndex;
        uint64 round;
    }

    uint256 public constant MAX_ROUND_TIME = 30 days; // Time at most 30 days from when round is first initiated, not when winning tickets are drawn

    IBlast public immutable BLAST;
    IERC20Rebasing public immutable WETH;
    IERC20Rebasing public immutable USDB;

    IEntropy private entropy;
    address private entropyProvider;

    bytes32 public root;
    uint256 public currentRound; // Increments by 1 every time the root is updated
    uint256 public currentTickets; // Resets to 0 every time the root is updated
    uint256 public maxPrizeCount;
    mapping(uint256 => uint256) public roundStart;
    mapping(address => uint256) public cumulativeTickets;
    mapping(address => mapping(uint256 => Round)) public entered; // Address => RoundIndex => Round
    mapping(uint256 => mapping(uint256 => Prize)) public prizes; // Need to keep track of prizes for each round. RoundIndex => PrizeIndex => Prize
    mapping(uint256 => mapping(uint256 => uint256[])) public winningTickets; // Need to keep track of winning tickets for each round. RoundIndex => PrizeIndex => WinningTickets
    mapping(uint64 => address) private requestedRandomNumber;

    /**
     *
     * @param _entropy - The address of the Entropy contract
     * @param _entropyProvider - The address of the entropy provider
     * @param _weth - The address of the WETH contract
     * @param _usdb - The address of the USDB contract
     */
    constructor(
        address _entropy,
        address _entropyProvider,
        address _blast,
        address _weth,
        address _usdb,
        uint256 _maxPrizeCount
    ) Ownable(msg.sender) {
        entropy = IEntropy(_entropy);
        entropyProvider = _entropyProvider;
        maxPrizeCount = _maxPrizeCount;
        BLAST = IBlast(_blast);
        WETH = IERC20Rebasing(_weth);
        USDB = IERC20Rebasing(_usdb);
        BLAST.configureAutomaticYield();
        BLAST.configureClaimableGas();
        WETH.configure(YieldMode.CLAIMABLE);
        USDB.configure(YieldMode.CLAIMABLE);
    }

    /**
     * Enter tickets into the current active round of Thruster Treasure.
     * @param _amount The amount of cumulative tickets the user has earned over time, based on merkle proof
     * @param _proof The Merkle proof to verify the user's tickets
     */
    function enterTickets(uint256 _amount, bytes32[] calldata _proof) external {
        uint256 currentRound_ = currentRound;
        require(winningTickets[currentRound_][0].length == 0, "ET");
        bytes32 node = keccak256(abi.encodePacked(msg.sender, _amount));
        require(MerkleProof.verify(_proof, root, node), "IP");
        uint256 ticketsToEnter = _amount - cumulativeTickets[msg.sender];
        require(ticketsToEnter > 0, "NTE");
        uint256 currentTickets_ = currentTickets;
        Round memory round = Round(currentTickets_, currentTickets_ + ticketsToEnter, currentRound_);
        entered[msg.sender][currentRound_] = round;
        cumulativeTickets[msg.sender] = _amount; // Ensure user can only enter tickets once, no partials
        currentTickets += ticketsToEnter;
        emit EnteredTickets(msg.sender, currentTickets_, currentTickets_ + ticketsToEnter, currentRound_);
    }

    /**
     * Claim prizes for a round
     * @param roundToClaim - The round to claim prizes for
     */
    function claimPrizesForRound(uint256 roundToClaim) external {
        require(roundStart[roundToClaim] + MAX_ROUND_TIME >= block.timestamp, "ICT");
        require(winningTickets[roundToClaim][0].length > 0, "NWT");
        Round memory round = entered[msg.sender][roundToClaim];
        require(round.ticketEnd > round.ticketStart, "NTE");
        uint256 maxPrizeCount_ = maxPrizeCount;
        for (uint256 i = 0; i < maxPrizeCount_; i++) {
            Prize memory prize = prizes[roundToClaim][i];
            uint256[] memory winningTicketsRoundPrize = winningTickets[roundToClaim][i];
            for (uint256 j = 0; j < winningTicketsRoundPrize.length; j++) {
                uint256 winningTicket = winningTicketsRoundPrize[j];
                if (round.ticketStart <= winningTicket && round.ticketEnd > winningTicket) {
                    _claimPrize(prize, msg.sender, winningTicket);
                }
            }
        }
        entered[msg.sender][roundToClaim] = Round(0, 0, roundToClaim); // Clear user's tickets for the round
        emit CheckedPrizesForRound(msg.sender, roundToClaim);
    }

    /**
     * Claims the prize for a user
     * @param _prize - The prize to claim
     * @param _winningTicket - The winning ticket number
     */
    function _claimPrize(Prize memory _prize, address _receiver, uint256 _winningTicket) internal {
        uint256 amountETH = _prize.amountWETH;
        uint256 amountUSDB = _prize.amountUSDB;
        WETH.transfer(_receiver, amountETH);
        USDB.transfer(_receiver, amountUSDB);
        emit ClaimedPrize(_receiver, _prize.round, _prize.prizeIndex, amountETH, amountUSDB, _winningTicket);
    }

    /**
     * Sets the maximum prize count
     * @param _maxPrizeCount - The new max prize count
     */
    function setMaxPrizeCount(uint256 _maxPrizeCount) external onlyOwner {
        maxPrizeCount = _maxPrizeCount;
        emit SetMaxPrizeCount(_maxPrizeCount);
    }

    /**
     * Claims the Blast native yield
     * @param _recipient - The address to claim the yield to
     * @param _amountWETH - The amount of WETH to claim
     * @param _amountUSDB - The amount of USDB to claim
     */
    function claimYield(address _recipient, uint256 _amountWETH, uint256 _amountUSDB) external onlyOwner {
        WETH.claim(_recipient, _amountWETH);
        USDB.claim(_recipient, _amountUSDB);
    }

    /**
     * Sets the prize for a round
     * @param _round - The round to set the prize for
     * @param _prizeIndex - The index of the prize to set
     * @param _amountWETH - The amount of WETH to set
     * @param _amountUSDB - The amount of USDB to set
     * @param _numWinners - The number of winners for the prize
     */
    function setPrize(uint256 _round, uint64 _prizeIndex, uint256 _amountWETH, uint256 _amountUSDB, uint64 _numWinners)
        external
        onlyOwner
    {
        require(_round >= currentRound, "ICR");
        require(_prizeIndex < maxPrizeCount, "IPC");
        depositPrize(msg.sender, _amountWETH, _amountUSDB);
        prizes[_round][_prizeIndex] = Prize(_amountWETH, _amountUSDB, _numWinners, _prizeIndex, uint64(_round));
    }

    /**
     * Deposits the prize amounts determined in setPrize
     *
     * @param _from - The address who should deposit the prize
     * @param _amountWETH - The amount of WETH
     * @param _amountUSDB - The amount of USDB
     */
    function depositPrize(address _from, uint256 _amountWETH, uint256 _amountUSDB) internal {
        WETH.transferFrom(_from, address(this), _amountWETH);
        USDB.transferFrom(_from, address(this), _amountUSDB);
        emit DepositedPrizes(_amountWETH, _amountUSDB);
    }

    /**
     * Retrieve tokens from the contract
     * @param _recipient - The address to retrieve the tokens to
     * @param _token - The address of the token to retrieve
     * @param _amount - The amount of tokens to retrieve
     */
    function retrieveTokens(address _recipient, address _token, uint256 _amount) external onlyOwner {
        IERC20Rebasing token = IERC20Rebasing(_token);
        if (_amount == 0) {
            _amount = token.balanceOf(address(this));
        }
        token.transfer(_recipient, _amount);
        emit WithdrawPrizes(_recipient, _token, _amount);
    }

    /**
     * Retrieve ETH from the contract
     * @param _recipient - The address to retrieve the ETH to
     * @param _amount - The amount of ETH to retrieve
     */
    function retrieveETH(address payable _recipient, uint256 _amount) external onlyOwner {
        if (_amount == 0) {
            _amount = address(this).balance;
        }
        _recipient.transfer(_amount);
        emit WithdrawPrizes(_recipient, address(0), _amount);
    }

    /**
     * Request many random numbers using Pyth Entropy
     * @param userCommitments - The user's commitments
     */
    function requestRandomNumberMany(bytes32[] calldata userCommitments)
        external
        payable
        onlyOwner
        returns (uint64[] memory seqNums)
    {
        uint256 fee = entropy.getFee(entropyProvider);
        require(address(this).balance >= fee * userCommitments.length, "IF");
        for (uint256 i = 0; i < userCommitments.length; i++) {
            uint64 sequenceNumber = entropy.request{value: fee}(entropyProvider, userCommitments[i], true);
            seqNums[i] = sequenceNumber;
            requestedRandomNumber[sequenceNumber] = msg.sender;
            emit RandomNumberRequest(sequenceNumber, userCommitments[i]);
        }
    }

    /**
     * Request a random number using Pyth Entropy
     * @param userCommitment - The user's commitment
     */
    function requestRandomNumber(bytes32 userCommitment) external payable onlyOwner returns (uint64) {
        uint256 fee = entropy.getFee(entropyProvider);
        require(address(this).balance > fee, "IF");

        uint64 sequenceNumber = entropy.request{value: fee}(entropyProvider, userCommitment, true);
        requestedRandomNumber[sequenceNumber] = msg.sender;

        emit RandomNumberRequest(sequenceNumber, userCommitment);
        return sequenceNumber;
    }

    /**
     * Sets the merkle root for the current round of Thruster Treasure
     * @param _root - The new root to set
     */
    function setRoot(bytes32 _root) external onlyOwner {
        root = _root;
        currentRound += 1;
        roundStart[currentRound] = block.timestamp;
        currentTickets = 0;
        emit NewRound(_root, currentRound);
    }

    /**
     *
     * @param _round - The round to claim the prize for
     * @param _prizeIndex - The index of the prize to claim
     * @param sequenceNumbers - The sequence numbers of the random number requests
     * @param userRandoms - The user random numbers
     * @param providerRandoms - The provider random numbers
     */
    function setWinningTickets(
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
        }
        winningTickets[_round][_prizeIndex] = _winningTickets;
        require(_winningTickets.length == numWinners, "WTL");
    }

    /**
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
    {
        require(currentTickets > 0, "NCT");
        // Reveal the random number. This call reverts if the provided values fail to match the commitments
        // from the request phase. If the call returns, randomNumber is a uniformly distributed bytes32.
        bytes32 randomNumber = entropy.reveal(entropyProvider, sequenceNumber, userRandom, providerRandom);
        uint256 randomTicket_ = uint256(randomNumber) % currentTickets;

        emit RandomNumberResult(randomTicket_, sequenceNumber);
        return randomTicket_;
    }

    /**
     * Claims the gas from the BLAST contract
     * @param _recipient - The address to claim the yield to
     * @param _minClaimRateBips - The minimum claim rate in bips
     */
    function claimGas(address _recipient, uint256 _minClaimRateBips) external onlyOwner returns (uint256 amount) {
        if (_minClaimRateBips == 0) {
            amount = BLAST.claimMaxGas(address(this), _recipient);
        } else {
            amount = BLAST.claimGasAtMinClaimRate(address(this), _recipient, _minClaimRateBips);
        }
        emit ClaimGas(_recipient, amount);
    }

    receive() external payable {}
}
