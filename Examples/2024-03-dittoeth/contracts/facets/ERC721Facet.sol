// SPDX-License-Identifier: GPL-3.0-only
pragma solidity 0.8.21;

import  {IERC721} from "../../node_modules/@openzeppelin/contracts/token/ERC721/IERC721.sol";
import  {IERC721Receiver} from "../../node_modules/@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";

import  {IDiamond} from "../../interfaces/IDiamond.sol";
import  {Events} from "../libraries/Events.sol";
import  {Errors} from "../libraries/Errors.sol";
import  {STypes, SR} from "../libraries/DataTypes.sol";
import  {Modifiers} from "../libraries/AppStorage.sol";
import  {LibDiamond} from "../libraries/LibDiamond.sol";
import  {LibSRUtil} from "../libraries/LibSRUtil.sol";

// import  {console} from "../libraries/console.sol";

contract ERC721Facet is Modifiers, IERC721 {
    /**
     * @dev Returns the number of tokens in ``owner``'s account.
     */
    function balanceOf(address owner) external view returns (uint256 balance) {
        if (owner == address(0)) revert Errors.ERC721InvalidOwner(address(0));

        address[] storage assets = s.assets;
        uint256 length = assets.length;
        for (uint256 i; i < length;) {
            STypes.ShortRecord[] memory shortRecords = IDiamond(payable(address(this))).getShortRecords(assets[i], owner);
            for (uint256 j; j < shortRecords.length;) {
                if (shortRecords[j].tokenId != 0) {
                    balance++;
                }
                unchecked {
                    j++;
                }
            }
            unchecked {
                ++i;
            }
        }
    }

    /**
     * @dev Returns whether `tokenId` exists.
     *
     * Tokens can be managed by their owner or approved accounts via {approve} or {setApprovalForAll}.
     *
     * Tokens start existing when they are minted (`_mint`),
     * and stop existing when they are burned (`_burn`).
     */
    function _exists(uint256 tokenId) internal view virtual returns (bool) {
        return _ownerOf(tokenId) != address(0);
    }

    /**
     * @dev Returns the owner of the `tokenId`. Does NOT revert if token doesn't exist
     */
    function _ownerOf(uint256 tokenId) internal view virtual returns (address) {
        return s.nftMapping[tokenId].owner;
    }

    /**
     * @dev Returns the owner of the `tokenId` token.
     *
     * Requirements:
     *
     * - `tokenId` must exist.
     */
    function ownerOf(uint256 tokenId) public view virtual returns (address) {
        address owner = _ownerOf(tokenId);
        if (owner == address(0)) revert Errors.ERC721NonexistentToken(tokenId);

        return owner;
    }

    /**
     * @dev Safely transfers `tokenId` token from `from` to `to`.
     *
     * Requirements:
     *
     * - `from` cannot be the zero address.
     * - `to` cannot be the zero address.
     * - `tokenId` token must exist and be owned by `from`.
     * - If the caller is not `from`, it must be approved to move this token by either {approve} or {setApprovalForAll}.
     * - If `to` refers to a smart contract, it must implement {IERC721Receiver-onERC721Received}, which is called upon a safe transfer.
     *
     * Emits a {Transfer} event.
     */
    function safeTransferFrom(address from, address to, uint256 tokenId) public virtual {
        safeTransferFrom(from, to, tokenId, "");
    }

    /**
     * @dev Safely transfers `tokenId` token from `from` to `to`, checking first that contract recipients
     * are aware of the ERC721 protocol to prevent tokens from being forever locked.
     *
     * Requirements:
     *
     * - `from` cannot be the zero address.
     * - `to` cannot be the zero address.
     * - `tokenId` token must exist and be owned by `from`.
     * - If the caller is not `from`, it must have been allowed to move this token by either {approve} or {setApprovalForAll}.
     * - If `to` refers to a smart contract, it must implement {IERC721Receiver-onERC721Received}, which is called upon a safe transfer.
     *
     * Emits a {Transfer} event.
     */
    function safeTransferFrom(address from, address to, uint256 tokenId, bytes memory data) public virtual {
        transferFrom(from, to, tokenId);

        if (!_checkOnERC721Received(from, to, tokenId, data)) revert Errors.ERC721InvalidReceiver(to);
    }

    /**
     * @dev Transfers `tokenId` token from `from` to `to`.
     *
     * WARNING: Note that the caller is responsible to confirm that the recipient is capable of receiving ERC721
     * or else they may be permanently lost. Usage of {safeTransferFrom} prevents loss, though the caller must
     * understand this adds an external call which potentially creates a reentrancy vulnerability.
     *
     * Requirements:
     *
     * - `from` cannot be the zero address.
     * - `to` cannot be the zero address.
     * - `tokenId` token must be owned by `from`.
     * - If the caller is not `from`, it must be approved to move this token by either {approve} or {setApprovalForAll}.
     *
     * Emits a {Transfer} event.
     */
    function transferFrom(address from, address to, uint256 tokenId) public {
        // @dev ensure the tokenId can be downcasted to 40 bits
        if (tokenId > type(uint40).max) revert Errors.InvalidTokenId();

        if (msg.sender != from && !s.isApprovedForAll[from][msg.sender] && msg.sender != s.getApproved[tokenId]) {
            revert Errors.ERC721InsufficientApproval(msg.sender, tokenId);
        }

        address owner = ownerOf(tokenId);
        if (owner != from) revert Errors.ERC721IncorrectOwner(from, tokenId, owner);

        if (to == address(0)) revert Errors.ERC721InvalidReceiver(address(0));

        // @dev If NFT does not exist, ERC721NonexistentToken() will trigger
        LibSRUtil.transferShortRecord(from, to, uint40(tokenId));

        delete s.getApproved[tokenId];

        emit Events.Transfer(from, to, tokenId);
    }

    /**
     * @dev Returns if the `operator` is allowed to manage all of the assets of `owner`.
     *
     * See {setApprovalForAll}
     */
    function isApprovedForAll(address owner, address operator) public view returns (bool) {
        return s.isApprovedForAll[owner][operator];
    }

    /**
     * @dev Gives permission to `to` to transfer `tokenId` token to another account.
     * The approval is cleared when the token is transferred.
     *
     * Only a single account can be approved at a time, so approving the zero address clears previous approvals.
     *
     * Requirements:
     *
     * - The caller must own the token or be an approved operator.
     * - `tokenId` must exist.
     *
     * Emits an {Approval} event.
     */
    function approve(address to, uint256 tokenId) external {
        // @dev ensure the tokenId can be downcasted to 40 bits
        if (tokenId > type(uint40).max) revert Errors.InvalidTokenId();

        address owner = _ownerOf(tokenId);
        if (to == owner) revert Errors.ERC721InvalidOperator(owner);
        if (msg.sender != owner && !isApprovedForAll(owner, msg.sender)) revert Errors.ERC721InvalidApprover(msg.sender);

        s.getApproved[tokenId] = to;

        emit Events.Approval(owner, to, tokenId);
    }

    /**
     * @dev Approve or remove `operator` as an operator for the caller.
     * Operators can call {transferFrom} or {safeTransferFrom} for any token owned by the caller.
     *
     * Requirements:
     *
     * - The `operator` cannot be the caller.
     *
     * Emits an {ApprovalForAll} event.
     */
    function setApprovalForAll(address operator, bool approved) external {
        if (msg.sender == operator) revert Errors.ERC721InvalidOperator(msg.sender);

        s.isApprovedForAll[msg.sender][operator] = approved;
        emit Events.ApprovalForAll(msg.sender, operator, approved);
    }

    /**
     * @dev Reverts if the `tokenId` has not been minted yet.
     */
    function _requireMinted(uint256 tokenId) internal view virtual {
        if (!_exists(tokenId)) revert Errors.ERC721NonexistentToken(tokenId);
    }

    /**
     * @dev Returns the account approved for `tokenId` token.
     *
     * Requirements:
     *
     * - `tokenId` must exist.
     */
    function getApproved(uint256 tokenId) external view returns (address operator) {
        _requireMinted(tokenId);
        return s.getApproved[tokenId];
    }

    /**
     * @notice Mints NFT for active shortRecord
     * @dev Minters can only mint their own shortRecords
     *
     * @param asset The market that will be impacted
     * @param shortRecordId Id of active shortRecord
     */
    function mintNFT(address asset, uint8 shortRecordId, uint16 shortOrderId)
        external
        isNotFrozen(asset)
        nonReentrant
        onlyValidShortRecord(asset, msg.sender, shortRecordId)
    {
        STypes.ShortRecord storage short = s.shortRecords[asset][msg.sender][shortRecordId];

        STypes.Order storage shortOrder = s.shorts[asset][shortOrderId];

        // @dev this is for transferShortRecord
        if (short.status == SR.PartialFill) {
            if (shortOrder.shortRecordId != shortRecordId || shortOrder.addr != msg.sender) revert Errors.InvalidShortOrder();
        } else {
            shortOrderId = 0;
        }

        if (short.tokenId != 0) revert Errors.AlreadyMinted();

        uint40 tokenId = s.tokenIdCounter;
        s.nftMapping[tokenId] = STypes.NFT({
            owner: msg.sender,
            assetId: s.asset[asset].assetId,
            shortRecordId: shortRecordId,
            shortOrderId: shortOrderId
        });

        short.tokenId = tokenId;

        // @dev never decreases
        s.tokenIdCounter += 1;
    }

    function tokenURI(uint256 id) public view virtual returns (string memory) {}

    /**
     * @dev Private function to invoke {IERC721Receiver-onERC721Received} on a target address.
     * The call is not executed if the target address is not a contract.
     *
     * @param from address representing the previous owner of the given token ID
     * @param to target address that will receive the tokens
     * @param tokenId uint256 ID of the token to be transferred
     * @param data bytes optional data to send along with the call
     * @return bool whether the call correctly returned the expected magic value
     */
    function _checkOnERC721Received(address from, address to, uint256 tokenId, bytes memory data) private returns (bool) {
        if (to.code.length > 0) {
            try IERC721Receiver(to).onERC721Received(msg.sender, from, tokenId, data) returns (bytes4 retval) {
                return retval == IERC721Receiver.onERC721Received.selector;
            } catch (bytes memory reason) {
                if (reason.length == 0) {
                    revert Errors.ERC721InvalidReceiver(to);
                } else {
                    /// @solidity memory-safe-assembly
                    // solhint-disable-next-line no-inline-assembly
                    assembly {
                        revert(add(32, reason), mload(reason))
                    }
                }
            }
        } else {
            return true;
        }
    }

    // This implements ERC-165 (copied from DiamondLoupeFacet.sol)
    function supportsInterface(bytes4 _interfaceId) external view returns (bool) {
        LibDiamond.DiamondStorage storage ds = LibDiamond.diamondStorage();
        return ds.supportedInterfaces[_interfaceId];
    }
}
