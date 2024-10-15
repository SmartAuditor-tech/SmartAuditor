// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity =0.5.16;

import "../../thruster-treasure/interfaces/IBlast.sol";
import "../interfaces/IThrusterYield.sol";
import "../../thruster-treasure/interfaces/IERC20Rebasing.sol";

contract ThrusterYield is IThrusterYield {
    IBlast public constant BLAST = IBlast(0x4300000000000000000000000000000000000002);
    IERC20Rebasing public constant USDB = IERC20Rebasing(0x4200000000000000000000000000000000000022);
    IERC20Rebasing public constant WETHB = IERC20Rebasing(0x4200000000000000000000000000000000000023);
    address public manager;

    event ClaimYieldAll(
        address indexed recipient, uint256 amountETH, uint256 amountWETH, uint256 amountUSDB, uint256 amountGas
    );
    event ClaimGas(address indexed recipient, uint256 amount);

    modifier onlyManager() {
        require(msg.sender == manager, "FORBIDDEN");
        _;
    }

    constructor(address _manager) public {
        BLAST.configureClaimableGas();
        BLAST.configureClaimableYield();
        USDB.configure(IERC20Rebasing.YieldMode.CLAIMABLE);
        WETHB.configure(IERC20Rebasing.YieldMode.CLAIMABLE);
        manager = _manager;
    }

    function claimYieldAll(address _recipient, uint256 _amountETH, uint256 _amountWETH, uint256 _amountUSDB)
        external
        onlyManager
        returns (uint256 amountETH, uint256 amountWETH, uint256 amountUSDB, uint256 amountGas)
    {
        amountETH = IBlast(BLAST).claimYield(address(this), _recipient, _amountETH);
        amountWETH = IERC20Rebasing(WETHB).claim(_recipient, _amountWETH);
        amountUSDB = IERC20Rebasing(USDB).claim(_recipient, _amountUSDB);
        amountGas = IBlast(BLAST).claimMaxGas(address(this), _recipient);
        emit ClaimYieldAll(_recipient, amountETH, amountWETH, amountUSDB, amountGas);
    }

    function claimGas(address _recipient, uint256 _minClaimRateBips) external onlyManager returns (uint256 amount) {
        if (_minClaimRateBips == 0) {
            amount = BLAST.claimMaxGas(address(this), _recipient);
        } else {
            amount = BLAST.claimGasAtMinClaimRate(address(this), _recipient, _minClaimRateBips);
        }
        emit ClaimGas(_recipient, amount);
    }

    function setManager(address _manager) external onlyManager {
        manager = _manager;
    }
}
