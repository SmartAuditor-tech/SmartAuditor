// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../../../node_modules/@openzeppelin/contracts-5.0/token/ERC20/extensions/IERC20Metadata.sol";

interface IPPrincipalToken is IERC20Metadata {
    function burnByYT(address user, uint256 amount) external;

    function mintByYT(address user, uint256 amount) external;

    function initialize(address _YT) external;

    function SY() external view returns (address);

    function YT() external view returns (address);

    function factory() external view returns (address);

    function expiry() external view returns (uint256);

    function isExpired() external view returns (bool);
}
