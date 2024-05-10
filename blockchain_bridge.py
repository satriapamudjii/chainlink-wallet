import os
from web3 import Web3

API_URL = os.getenv('API_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
PUBLIC_KEY = os.getenv('PUBLIC_KEY')

web3 = Web3(Web3.HTTPProvider(API_URL))

class BlockchainBridge:
    supported_chains = ['Ethereum', 'BinanceSmartChain']

    def __init__(self):
        self.private_key = PRIVATE_KEY
        self.public_key = PUBLIC_KEY

    def transfer_asset(self, from_chain, to_chain, asset, amount, receiver):
        if not all([self.is_chain_supported(chain) for chain in [from_chain, to_chain]]):
            print(f'Chain(s) not supported: {from_chain}, {to_chain}. Only supports: {self.supported_chains}')
            return False
        print(f'Transferring {amount} {asset} from {from_chain} to {to_chain}. Receiver: {receiver}')
        return True

    def is_chain_supported(self, chain):
        return chain in self.supported_chains

if __name__ == '__main__':
    bridge = BlockchainBridge()
    bridge.transfer_asset('Ethereum', 'BinanceSmartChain', 'ETH', 1, '0xReceiverAddress')