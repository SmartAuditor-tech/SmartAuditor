// SPDX-License-Identifier: GPL-3.0-only
pragma solidity 0.8.21;

import  {U256, U80} from "../libraries/PRBMathHelper.sol";

import  {Errors} from "../libraries/Errors.sol";
import  {STypes, MTypes, O} from "../libraries/DataTypes.sol";
import  {Modifiers} from "../libraries/AppStorage.sol";
import  {LibAsset} from "../libraries/LibAsset.sol";
import  {LibOrders} from "../libraries/LibOrders.sol";

// import  {console} from "../libraries/console.sol";

contract AskOrdersFacet is Modifiers {
    using U256 for uint256;
    using U80 for uint80;

    /**
     * @notice Creates ask order in market
     * @dev IncomingAsk created here instead of AskMatchAlgo to prevent stack too deep
     *
     * @param asset The market that will be impacted
     * @param price Unit price in eth for erc sold
     * @param ercAmount Amount of erc sold
     * @param isMarketOrder Boolean for whether the ask is limit or market
     * @param orderHintArray Array of hint ID for gas-optimized sorted placement on market
     */
    function createAsk(
        address asset,
        uint80 price,
        uint88 ercAmount,
        bool isMarketOrder,
        MTypes.OrderHint[] calldata orderHintArray
    ) external isNotFrozen(asset) onlyValidAsset(asset) nonReentrant {
        uint256 eth = price.mul(ercAmount);
        uint256 minAskEth = LibAsset.minAskEth(asset);
        if (eth < minAskEth) revert Errors.OrderUnderMinimumSize();

        if (s.assetUser[asset][msg.sender].ercEscrowed < ercAmount) revert Errors.InsufficientERCEscrowed();

        STypes.Order memory incomingAsk;
        incomingAsk.addr = msg.sender;
        incomingAsk.price = price;
        incomingAsk.ercAmount = ercAmount;
        incomingAsk.id = s.asset[asset].orderIdCounter;
        incomingAsk.orderType = isMarketOrder ? O.MarketAsk : O.LimitAsk;
        incomingAsk.creationTime = LibOrders.getOffsetTime();

        // @dev asks don't need to be concerned with shortHintId
        LibOrders.sellMatchAlgo(asset, incomingAsk, orderHintArray, minAskEth);
    }

    // @dev contract size limit for BidOrdersFacet
    function _cancelAsk(address asset, uint16 id) external onlyDiamond {
        LibOrders.cancelAsk(asset, id);
    }

    // @dev contract size limit for BidOrdersFacet
    function _cancelShort(address asset, uint16 id) external onlyDiamond {
        LibOrders.cancelShort(asset, id);
    }
}
