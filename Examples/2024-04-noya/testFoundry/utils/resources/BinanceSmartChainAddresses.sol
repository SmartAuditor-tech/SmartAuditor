// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.20;

import  { ERC20 } from "../../../node_modules/@openzeppelin/contracts-5.0/token/ERC20/ERC20.sol";

contract BinanceSmartChainAddresses {
    // DeFi Ecosystem
    address public ETH = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;
    address public uniV3Router = 0xE592427A0AEce92De3Edee1F18E0157C05861564;
    address public uniV2Router = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;

    // ERC20s
    ERC20 public USDC = ERC20(0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359);
    ERC20 public USDCe = ERC20(0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174);
    ERC20 public WETH = ERC20(0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619);
    ERC20 public WBTC = ERC20(0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6);
    ERC20 public USDT = ERC20(0xc2132D05D31c914a87C6611C10748AEb04B58e8F);
    ERC20 public DAI = ERC20(0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063);
    ERC20 public WSTETH = ERC20(0x03b54A6e9a984069379fae1a4fC4dBAE93B3bCCD);
    ERC20 public CBETH = ERC20(address(0));
    ERC20 public FRAX = ERC20(0x104592a158490a9228070E0A8e5343B499e125D0);
    ERC20 public COMP = ERC20(0x8505b9d2254A7Ae468c0E9dd10Ccea3A837aef5c);
    ERC20 public LINK = ERC20(0xb0897686c545045aFc77CF20eC7A532E3120E0F1);
    ERC20 public LINKe = ERC20(0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39);
    ERC20 public MATICx = ERC20(0xfa68FB4628DFF1028CFEc22b4162FCcd0d45efb6);
    ERC20 public stMATIC = ERC20(0x3A58a54C066FdC0f2D55FC9C89F0415C92eBf3C4);
    ERC20 public WMATIC = ERC20(0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270);

    // Chainlink Datafeeds
    address public WETH_USD_FEED = 0xF9680D99D6C9589e2a93a78A04A279e509205945;
    address public USDC_USD_FEED = 0xfE4A8cc5b5B2366C1B58Bea3858e81843581b2F7;
    address public USDCe_USD_FEED = 0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3;
    address public WBTC_USD_FEED = 0xDE31F8bFBD8c84b5360CFACCa3539B938dd78ae6;
    address public DAI_USD_FEED = 0x4746DeC9e833A82EC7C2C1356372CcF2cfcD2F3D;
    address public USDT_USD_FEED = 0x0A6513e40db6EB1b165753AD52E80663aeA50545;
    address public COMP_USD_FEED = 0x2A8758b7257102461BC958279054e372C2b1bDE6;
    address public FRAX_USD_FEED = 0x00DBeB1e45485d53DF7C2F0dF1Aa0b6Dc30311d3;
    address public WSTETH_ETH_FEED = 0x10f964234cae09cB6a9854B56FF7D4F38Cda5E6a;
    address public CBETH_ETH_FEED = 0x0a6a03CdF7d0b48d4e4BA8e362A4FfC3aAC4f3c0;
    address public BAL_USD_FEED = 0xD106B538F2A868c28Ca1Ec7E298C3325E0251d66;
    address public UNI_USD_FEED = 0xdf0Fb4e4F928d2dCB76f438575fDD8682386e13C;
    address public CRV_USD_FEED = 0x336584C8E6Dc19637A5b36206B1c79923111b405;
    address public LINK_USD_FEED = 0xd9FFdb71EbE7496cC440152d43986Aae0AB76665;
    address public LINK_ETH_FEED = 0xb77fa460604b9C6435A235D057F7D319AC83cb53;
    address public MATICx_USD_FEED = 0x5d37E4b374E6907de8Fc7fb33EE3b0af403C7403;
    address public stMATIC_USD_FEED = 0x97371dF4492605486e23Da797fA68e55Fc38a13f;
    address public MATIC_USD_FEED = 0xAB594600376Ec9fD91F8e885dADF0CE036862dE0;
    address public MATIC_ETH_FEED = 0x327e23A4855b6F663a28c5161541d69Af8973302;

    // Aave V3 Tokens
    ERC20 public aV3USDC = ERC20(address(0));
    ERC20 public dV3USDC = ERC20(address(0));
    ERC20 public aV3USDCe = ERC20(0x625E7708f30cA75bfd92586e17077590C60eb4cD);
    ERC20 public dV3USDCe = ERC20(0xFCCf3cAbbe80101232d343252614b6A3eE81C989);
    ERC20 public aV3WETH = ERC20(0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8);
    ERC20 public dV3WETH = ERC20(0x0c84331e39d6658Cd6e6b9ba04736cC4c4734351);
    ERC20 public aV3WBTC = ERC20(0x078f358208685046a11C85e8ad32895DED33A249);
    ERC20 public dV3WBTC = ERC20(0x92b42c66840C7AD907b4BF74879FF3eF7c529473);
    ERC20 public aV3USDT = ERC20(0x6ab707Aca953eDAeFBc4fD23bA73294241490620);
    ERC20 public dV3USDT = ERC20(0xfb00AC187a8Eb5AFAE4eACE434F493Eb62672df7);
    ERC20 public aV3DAI = ERC20(0x82E64f49Ed5EC1bC6e43DAD4FC8Af9bb3A2312EE);
    ERC20 public dV3DAI = ERC20(0x8619d80FB0141ba7F184CbF22fd724116D9f7ffC);
    ERC20 public aV3WSTETH = ERC20(0xf59036CAEBeA7dC4b86638DFA2E3C97dA9FcCd40);
    ERC20 public dV3WSTETH = ERC20(0x77fA66882a8854d883101Fb8501BD3CaD347Fc32);
    ERC20 public aV3WMATIC = ERC20(0x6d80113e533a2C0fe82EaBD35f1875DcEA89Ea97);
    ERC20 public dV3WMATIC = ERC20(0x4a1c3aD6Ed28a636ee1751C69071f6be75DEb8B8);
    ERC20 public aV3LINK = ERC20(0x191c10Aa4AF7C30e871E70C95dB0E4eb77237530);
    ERC20 public dV3LINK = ERC20(0x953A573793604aF8d41F306FEb8274190dB4aE0e);
    ERC20 public aV3MATICx = ERC20(0x80cA0d8C38d2e2BcbaB66aA1648Bd1C7160500FE);
    ERC20 public dV3MATICx = ERC20(0xB5b46F918C2923fC7f26DB76e8a6A6e9C4347Cf9);
    ERC20 public aV3stMATIC = ERC20(0xEA1132120ddcDDA2F119e99Fa7A27a0d036F7Ac9);

    // Balancer V2 Addresses

    // Chainlink Automation Registry
    address public automationRegistry = 0x08a8eea76D2395807Ce7D1FC942382515469cCA1;
    address public automationRegistrar = 0x0Bc5EDC7219D272d9dEDd919CE2b4726129AC02B;

    // FraxLend Pairs

    // Curve Pools and Tokens

    // Convex-Curve Platform Specifics

    // Uniswap V3

    // Redstone
}
