from brownie import (
    accounts,
    NFTDescriptor,
    NonfungibleTokenPositionDescriptor,
    NonfungiblePositionManager,
    ThrusterMulticall,
    SwapRouter,
    ThrusterPoolFactory,
    ThrusterPoolDeployer,
    TickLens,
    QuoterV2,
)

def main():
    deployer = accounts.load('YOUR_ACCOUNT')
    
    WETHB = "0x4200000000000000000000000000000000000023"

    # Deploying the ThrusterPoolFactory
    factory = ThrusterPoolFactory.deploy(deployer, deployer, {'from': deployer})
    poolDeployer = ThrusterPoolDeployer.deploy(factory, {'from': deployer})
    factory.setDeployer(poolDeployer, {'from': deployer})

    # Deploy Multicall
    multicall = ThrusterMulticall.deploy(deployer, {'from': deployer})

    # Deploy TickLens
    tick_lens = TickLens.deploy({'from': deployer})

    # Deploy NFT Descriptor Library
    nft_descriptor = NFTDescriptor.deploy({'from': deployer})
    eth_bytes = "0x4554480000000000000000000000000000000000000000000000000000000000"
    nft_pd = NonfungibleTokenPositionDescriptor.deploy(WETHB, eth_bytes, {'from': deployer})

    # Deploy PositionManager
    nft_pm = NonfungiblePositionManager.deploy(poolDeployer, WETHB, nft_pd, deployer, {'from': deployer})    

    # Deploy Quoter
    quoter = QuoterV2.deploy(poolDeployer, WETHB, {'from': deployer})

    # Deploy Router
    router = SwapRouter.deploy(poolDeployer, WETHB, deployer, {'from': deployer})

    print("Factory deployed at:", factory.address)
    print("PoolDeployer deployed at:", poolDeployer.address)
    print("Multicall deployed at:", multicall.address)
    print("TickLens deployed at:", tick_lens.address)
    print("NFTDescriptor deployed at:", nft_descriptor.address)
    print("NFTPositionDescriptor deployed at:", nft_pd.address)
    print("NFTPositionManager deployed at:", nft_pm.address)
    print("Quoter deployed at:", quoter.address)
    print("Router deployed at:", router.address)

