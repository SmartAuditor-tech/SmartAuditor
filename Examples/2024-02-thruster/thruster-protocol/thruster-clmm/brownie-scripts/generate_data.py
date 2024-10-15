from brownie import (
    accounts,
    NonfungiblePositionManager,
    SwapRouter,
    interface,
    chain,
)
import math

def main():
    manager = NonfungiblePositionManager.at("") # Deployed NonfungiblePositionManager address 
    router = SwapRouter.at("") # Deployed SwapRouter address

    me = accounts.load('YOUR_ACCOUNT')

    USDB = "0x4200000000000000000000000000000000000022"
    WETH = "0x4200000000000000000000000000000000000023"

    tokens = [WETH, USDB]
    interface.IWETH9(WETH).deposit({'from': me, 'value': 0.01e18})
    nft_pos_id = 1 # NEED TO MODIFY THIS FOR DECREASE LIQUIDITY AND COLLECT, assumes you are first
    for t in tokens:
        token = interface.ERC20(t)
        token.approve(manager, 2**256 - 1, {'from': me})
        token.approve(router, 2**256 - 1, {'from': me})

    # The below is populated with dummy values, you can adjust them as needed
    init_price = 1/2700 # 2000 usd fo eth
    high_tick = math.floor(price_to_tick(1/2500)/10) * 10 # 10 is for tick spacing of the 500 fee pool tier
    low_tick = math.ceil(price_to_tick(1/3500)/10) * 10

    manager.createAndInitializePoolIfNecessary(USDB, WETH, 500, price_to_sqrtp(init_price), {'from': me})
    manager.mint((USDB, WETH, 500, low_tick, high_tick, 27e18, 0.01e18, 0, 0, me, chain.time()+100), {'from': me})
    path = '0x' + WETH[2:] + '0001f4' + USDB[2:]
    router.exactInput((path, me, chain.time()+100, 0.1e18, 0), {'from': me})
    manager.decreaseLiquidity((nft_pos_id, 76334861509435, 0, 0, chain.time()+100), {'from': me})
    manager.collect((nft_pos_id, me, 2**128-1, 2**128-1), {'from': me})
    
def price_to_sqrtp(price):
    return int(math.sqrt(price) * 2**96)

def price_to_tick(p):
    return math.floor(math.log(p, 1.0001))
