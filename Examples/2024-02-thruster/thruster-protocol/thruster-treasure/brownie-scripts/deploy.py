from brownie import (
    a,
    ThrusterTreasure,
)


def main():
    entropy = '0x98046Bd286715D3B0BC227Dd7a956b83D8978603'
    provider = '0x6CC14824Ea2918f5De5C2f75A9Da968ad4BD6344'
    blast = '0x4300000000000000000000000000000000000002'
    weth = '0x4200000000000000000000000000000000000023'
    usdb = '0x4200000000000000000000000000000000000022'
    maxprizecount = 4

    me = a.load('YOUR_ACCOUNT')

    tt = ThrusterTreasure.deploy(
        entropy, provider, blast, weth, usdb, maxprizecount, {'from': me})

    root = '0x84ab5d988041be305b45fa5b4dd7cdb63c5965127b8531008a336d96e438892a' # Root is dependent on your addresses

    tt.setRoot(root, {'from': me})

    tt.setPrize(1, 0, 0.001e18, 0, 2, {'from': me})

    me_amt = 300
    me_proofs = ['0x00f1a0ccb57522a4a8517e507def05aa1bd5ac8cc46b4b5d0c93599573258fc6',
                 '0x48585e7333b686a458b8e06910e9ec26de727a310803608da7c21ef345844c0b']

    tt.enterTickets(me_amt, me_proofs, {'from': me})

    me2 = a.load('YOUR_OTHER_ACCOUNT')
    me2_proofs = ['0x2868ce0f3ea4af758e3a2d38e0eaf91871f9ac2532d0e07d18d321cd52afad2f',
                  '0x48585e7333b686a458b8e06910e9ec26de727a310803608da7c21ef345844c0b']
    me2_amt = 10000
    tt.enterTickets(me2_amt, me2_proofs, {'from': me2})

    print("ThrusterTreasure,", tt.address)
    print("currentTickets", tt.currentTickets())
    print("my tickets", tt.entered(me, 1))
    print("m2 tickets", tt.entered(me2, 1))
