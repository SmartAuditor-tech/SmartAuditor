// SPDX-License-Identifier: MIT
pragma solidity = 0.8.17;

interface IVault {
  event Withdraw (uint indexed from, address indexed to, uint amount);
  event Deposit  (uint indexed id, uint amount);
  event Move     (uint indexed from, uint indexed to, uint amount);

  error StaleData            ();
  error IncompleteRound      ();
  error NotVaultManager      ();

  // A vault must implement these functions
  function deposit    (uint id, uint amount) external;
  function move       (uint from, uint to, uint amount) external;
  function withdraw   (uint id, address to, uint amount) external;
  function getUsdValue(uint id) external view returns (uint);
}
