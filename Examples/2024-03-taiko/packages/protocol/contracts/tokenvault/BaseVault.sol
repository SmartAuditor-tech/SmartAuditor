// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "../../node_modules/@openzeppelin/contracts-upgradeable/utils/introspection/IERC165Upgradeable.sol";
import "../../node_modules/@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import "../bridge/IBridge.sol";
import "../common/EssentialContract.sol";

/// @title BaseVault
/// @notice This abstract contract provides a base implementation for vaults.
/// @custom:security-contact security@taiko.xyz
abstract contract BaseVault is
    EssentialContract,
    IRecallableSender,
    IMessageInvocable,
    IERC165Upgradeable
{
    uint256[50] private __gap;

    error VAULT_PERMISSION_DENIED();

    modifier onlyFromBridge() {
        if (msg.sender != resolve("bridge", false)) {
            revert VAULT_PERMISSION_DENIED();
        }
        _;
    }

    /// @notice Initializes the contract.
    /// @param _owner The owner of this contract. msg.sender will be used if this value is zero.
    /// @param _addressManager The address of the {AddressManager} contract.
    function init(address _owner, address _addressManager) external initializer {
        __Essential_init(_owner, _addressManager);
    }

    /// @notice Checks if the contract supports the given interface.
    /// @param _interfaceId The interface identifier.
    /// @return true if the contract supports the interface, false otherwise.
    function supportsInterface(bytes4 _interfaceId) public view virtual override returns (bool) {
        return _interfaceId == type(IRecallableSender).interfaceId;
    }

    /// @notice Returns the name of the vault.
    /// @return The name of the vault.
    function name() public pure virtual returns (bytes32);

    function checkProcessMessageContext()
        internal
        view
        onlyFromBridge
        returns (IBridge.Context memory ctx_)
    {
        ctx_ = IBridge(msg.sender).context();
        address selfOnSourceChain = resolve(ctx_.srcChainId, name(), false);
        if (ctx_.from != selfOnSourceChain) revert VAULT_PERMISSION_DENIED();
    }

    function checkRecallMessageContext()
        internal
        view
        onlyFromBridge
        returns (IBridge.Context memory ctx_)
    {
        ctx_ = IBridge(msg.sender).context();
        if (ctx_.from != msg.sender) revert VAULT_PERMISSION_DENIED();
    }
}
