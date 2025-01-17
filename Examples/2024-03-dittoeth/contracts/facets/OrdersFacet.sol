// SPDX-License-Identifier: GPL-3.0-only
pragma solidity 0.8.21;

import  {U256, U88} from "../libraries/PRBMathHelper.sol";

import  {Modifiers} from "../libraries/AppStorage.sol";
import  {Errors} from "../libraries/Errors.sol";
import  {STypes, O} from "../libraries/DataTypes.sol";
import  {LibOrders} from "../libraries/LibOrders.sol";
import  {C} from "../libraries/Constants.sol";

// import  {console} from "../libraries/console.sol";

contract OrdersFacet is Modifiers {
    using U256 for uint256;
    using U88 for uint88;
    using LibOrders for mapping(address => mapping(uint16 => STypes.Order));

    /**
     * @notice Cancels unfilled bid on market
     *
     * @param asset The market that will be impacted
     * @param id Id of bid
     */
    function cancelBid(address asset, uint16 id) external onlyValidAsset(asset) nonReentrant {
        STypes.Order storage bid = s.bids[asset][id];
        if (msg.sender != bid.addr) revert Errors.NotOwner();

        LibOrders.cancelBid(asset, id);
    }

    /**
     * @notice Cancels unfilled ask on market
     *
     * @param asset The market that will be impacted
     * @param id Id of ask
     */
    function cancelAsk(address asset, uint16 id) external onlyValidAsset(asset) nonReentrant {
        STypes.Order storage ask = s.asks[asset][id];
        if (msg.sender != ask.addr) revert Errors.NotOwner();

        LibOrders.cancelAsk(asset, id);
    }

    /**
     * @notice Cancels unfilled short on market
     *
     * @param asset The market that will be impacted
     * @param id Id of short
     */
    function cancelShort(address asset, uint16 id) external onlyValidAsset(asset) nonReentrant {
        STypes.Order storage short = s.shorts[asset][id];
        if (msg.sender != short.addr) revert Errors.NotOwner();

        LibOrders.cancelShort(asset, id);
    }

    /**
     * @notice Used to clear orderbook and/or to prevent DOS
     *
     * @param asset The market that will be impacted
     * @param orderType Order type to be cancelled
     * @param lastOrderId Id of the order in the last position, farthest from HEAD
     * @param numOrdersToCancel Number of orders to cancel, includinf the lastOrderId
     */
    function cancelOrderFarFromOracle(address asset, O orderType, uint16 lastOrderId, uint16 numOrdersToCancel)
        external
        onlyAdminOrDAO
        onlyValidAsset(asset)
        nonReentrant
    {
        if (s.asset[asset].orderIdCounter < 65000) revert Errors.OrderIdCountTooLow();

        if (numOrdersToCancel > 1000) revert Errors.CannotCancelMoreThan1000Orders();

        if (orderType == O.LimitBid && s.bids[asset][lastOrderId].nextId == C.TAIL) {
            cancelManyBids(asset, lastOrderId, numOrdersToCancel);
        } else if (orderType == O.LimitAsk && s.asks[asset][lastOrderId].nextId == C.TAIL) {
            cancelManyAsks(asset, lastOrderId, numOrdersToCancel);
        } else if (orderType == O.LimitShort && s.shorts[asset][lastOrderId].nextId == C.TAIL) {
            cancelManyShorts(asset, lastOrderId, numOrdersToCancel);
        } else {
            revert Errors.NotLastOrder();
        }
    }

    function cancelManyBids(address asset, uint16 lastOrderId, uint16 numOrdersToCancel) internal {
        uint16 prevId;
        uint16 currentId = lastOrderId;
        for (uint8 i; i < numOrdersToCancel;) {
            prevId = s.bids[asset][currentId].prevId;
            LibOrders.cancelBid(asset, currentId);
            currentId = prevId;
            unchecked {
                ++i;
            }
        }
    }

    function cancelManyAsks(address asset, uint16 lastOrderId, uint16 numOrdersToCancel) internal {
        uint16 prevId;
        uint16 currentId = lastOrderId;
        for (uint8 i; i < numOrdersToCancel;) {
            prevId = s.asks[asset][currentId].prevId;
            LibOrders.cancelAsk(asset, currentId);
            currentId = prevId;
            unchecked {
                ++i;
            }
        }
    }

    function cancelManyShorts(address asset, uint16 lastOrderId, uint16 numOrdersToCancel) internal {
        uint16 prevId;
        uint16 currentId = lastOrderId;
        for (uint8 i; i < numOrdersToCancel;) {
            prevId = s.shorts[asset][currentId].prevId;
            LibOrders.cancelShort(asset, currentId);
            currentId = prevId;
            unchecked {
                ++i;
            }
        }
    }
}
