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
        if self.validate_chains(from_chain, to_chain):
            self.initiate_transfer(from_chain, to_chain, asset, amount, receiver)
        else:
            self.display_chain_error(from_chain, to_chain)

    def validate_chains(self, from_chain, to_chain):
        return all([self.is_chain_supported(chain) for chain in [from_chain, to_chain]])

    def initiate_transfer(self, from_chain, to_chain, asset, amount, receiver):
        print(f'Transferring {amount} {asset} from {from_chain} to {to_chain}. Receiver: {receiver}')
        return True

    def display_chain_error(self, from_chain, to_chain):
        print(f'Chain(s) not supported: {from_chain}, {to_chain}. Only supports: {self.supported_chains}')
        return False

    def is_chain_supported(self, chain):
        return chain in self.supported_chains

if __name__ == '__main__':
    bridge = BlockchainBridge()
    bridge.transfer_asset('Ethereum', 'BinanceSmartChain', 'ETH', 1, '0xReceiverAddress')