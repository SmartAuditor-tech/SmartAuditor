from brownie import (
    accounts,
    ThrusterFactory,
    ThrusterRouter,
    interface,
)

def main():
    deployer = accounts.load('YOUR_ACCOUNT')

    factory = ThrusterFactory.at("") # Deployed ThrusterFactory address
    router = ThrusterRouter.at("") # Deployed ThursterRouter address

    USDB = "0x4200000000000000000000000000000000000022"
    WETH = "0x4200000000000000000000000000000000000023"

    tokens = [WETH, USDB]
    tmap = {WETH: 'WETH', USDB: 'USDB'}
    pairs = []

    # Wrap some ETH to WETH first to add liquidity
    weth = interface.IWETH(WETH)
    weth.deposit({'from': deployer, 'value': "0.01 ether"})

    for t in tokens:
        token = interface.IERC20(t)
        token.approve(router, 2**256-1, {'from': deployer})

    for t1 in range(len(tokens)):
        for t2 in range(t1+1, len(tokens)):
            # factory.createPair(tokens[t1], tokens[t2], {'from': deployer})
            amount0 = 0.01e18 
            amount1 = 27e18
            if tokens[t1] == WETH:
                router.addLiquidityETH(
                    tokens[t2],
                    amount1,
                    0,
                    0,
                    deployer,
                    2**256-1,
                    {'from': deployer, 'value': amount0}
                )
            elif tokens[t2] == WETH:
                router.addLiquidityETH(
                    tokens[t1],
                    amount0,
                    0,
                    0,
                    deployer,
                    2**256-1,
                    {'from': deployer, 'value': amount1}
                )
            else:
                router.addLiquidity(
                    tokens[t1],
                    tokens[t2],
                    amount0,
                    amount1,
                    0,
                    0,
                    deployer,
                    2**256-1,
                    {'from': deployer}
                )
            pair = factory.getPair(tokens[t1], tokens[t2])
            pairs.append(pair)

    for pair in pairs:
        pair0 = interface.IThrusterPair(pair).token0()
        pair1 = interface.IThrusterPair(pair).token1()
        print(tmap[pair0], tmap[pair1], pair)
