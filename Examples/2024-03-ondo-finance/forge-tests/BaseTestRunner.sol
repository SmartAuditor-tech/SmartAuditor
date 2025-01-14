pragma solidity 0.8.16;

import "MinimalTestRunner.sol";
import "helpers/Constants.sol";
import "helpers/DeltaCheckHarness.sol";
import "../contracts/interfaces/IRWALike.sol";

abstract contract BaseTestRunner is MinimalTestRunner, Oracles {
  // RWAHub constants
  bytes32 public constant FIRST_DEPOSIT_ID = bytes32(uint256(1));
  bytes32 public constant SECOND_DEPOSIT_ID = bytes32(uint256(2));
  bytes32 public constant FIRST_REDEMPTION_ID = bytes32(uint256(1));
  bytes32 public constant SECOND_REDEMPTION_ID = bytes32(uint256(2));

  // Pointer to variables to use in generalized RWAHub tests
  RWAHub rwaHub;
  IRWALike rwa;
  Pricer pricer;
  DeltaCheckHarness oracleCheckHarness; // Use delta check harness for time being

  // Pointer to helper variables used by generalized RWAHub tests
  bytes32[] depositIds;
  uint256[] priceIds;

  bytes32[] txnHashes;
  bytes32[] redemptionIds;

  // Users array for multi-user tests
  address[] users;

  /*//////////////////////////////////////////////////////////////
                            KYC Registry
  //////////////////////////////////////////////////////////////*/

  KYCRegistry registry;

  function _deployKYCRegistry() internal {
    // Make sure we don't redeploy for multi-token integration tests
    if (address(registry) == address(0)) {
      registry = new KYCRegistry(address(this), address(SANCTIONS_ORACLE));
    }
  }

  function _addAddressToKYC(uint256 level, address account) internal {
    address[] memory addressesToKYC = new address[](1);
    addressesToKYC[0] = account;
    registry.addKYCAddresses(level, addressesToKYC);
  }

  function _removeAddressFromKYC(uint256 level, address account) internal {
    address[] memory addressesToRemoveKYC = new address[](1);
    addressesToRemoveKYC[0] = account;
    registry.removeKYCAddresses(level, addressesToRemoveKYC);
  }

  /*//////////////////////////////////////////////////////////////
                             Helpers
  //////////////////////////////////////////////////////////////*/

  function _seedWithCollateral(address _user, uint256 amount) public {
    deal(address(USDC), _user, amount);
  }

  function _setRwaHub(address _rwaHub) internal {
    rwaHub = RWAHub(_rwaHub);
  }

  function _setRwa(address _rwa) internal {
    rwa = IRWALike(_rwa);
  }

  function _setPricer(address _pricer) internal {
    pricer = Pricer(_pricer);
  }

  function _setOracleCheckHarness(address _oracleCheckHarness) internal {
    oracleCheckHarness = DeltaCheckHarness(_oracleCheckHarness);
  }

  function _mintRWAToUser(address _user, uint256 depositAmount) internal {
    vm.prank(guardian);
    rwa.mint(_user, depositAmount);
  }

  modifier postClaimState(address user, uint256 amt) {
    _mintRWAToUser(user, amt);
    _;
  }
}

contract User {}
