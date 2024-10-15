from brownie import (
    accounts,
    ThrusterFactory,
    ThrusterRouter,
)

def main():
    deployer = accounts.load('YOUR_ACCOUNT')

    WETH = "0x4200000000000000000000000000000000000023"

    yieldToSetter = deployer.address
    factory = ThrusterFactory.deploy(yieldToSetter, yieldToSetter, {'from': deployer})

    router = ThrusterRouter.deploy(factory, WETH, {'from': deployer})

    print("ThrusterFactory deployed to:", factory.address)
    print("ThrusterRouter deployed to:", router.address)
