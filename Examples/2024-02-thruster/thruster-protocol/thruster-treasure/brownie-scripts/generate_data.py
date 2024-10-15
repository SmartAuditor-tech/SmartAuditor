from brownie import (
    a,
    ThrusterTreasure,
    interface,
)

import requests
import secrets
from eth_utils import keccak


def main():
    me = a.load('YOUR_ACCCOUNT')
    tt = ThrusterTreasure.at('') # Deployed ThrusterTreasure address
    FEE = 101  # fee is always 101 wei for now
    currRound = 1
    prizeIdx = 0

    commitments = []
    random_numbers = []
    for _ in range(2):
        random_number = '0x' + secrets.token_hex(32) # Need to add 0x in front to make it all work
        commitment = '0x' + keccak(hexstr=random_number).hex() # Convert keccak bytes to hex string and add 0x in front
        random_numbers.append(random_number)
        commitments.append(commitment)
    # Request random number
    print(random_numbers)
    tt.requestRandomNumberMany(commitments, {'from': me, 'value': FEE * len(commitments)}).return_value

    # keep the random numbers generated
    random_numbers = ['0x6abd450163bd7d826fdfae422e0e0437bbdf66227008061c1be77bfbcedd087f',
                      '0xaddd3bc7ff5671833da6b95104930a77609cf255e9045244872e112dabd4f91a']
    # Client doesn't support return value so need to check logs for seqNums
    seqNums = [827, 828]

    provider_numbers = []
    for seqNum in seqNums:
        res = requests.get(
            f'https://fortuna-staging.pyth.network/v1/chains/blast-testnet/revelations/{seqNum}')
        provider_number = '0x' + res.json()['value']['data']
        provider_numbers.append(provider_number)

    tt.setWinningTickets(currRound, prizeIdx, seqNums,
                         random_numbers, provider_numbers, {'from': me})

    # print(rrn.return_value) # return value doesn't work on blast node
