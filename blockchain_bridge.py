import json
import os
from web3 import Web3

API_URL = os.getenv("API_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")

web3 = Web3(Web3.HTTPProvider(API_URL))

class BlockchainBridge:
    def __init__(self):
        self.private_key = PRIVATE_KEY
        self.public_key = PUBLIC_KEY

    def transfer_asset(self, from_chain, to_chain, asset, amount, receiver):
        
        if not self.is_chain_supported(from_chain) or not self.is_chain_supported(to_chain):
            print(f"Chain(s) not supported: {from_chain}, {to_chain}")
            return False
        
        print(f"Transferring {amount} {asset} from {from_chain} to {to_chain}, receiver {receiver}")
        return True

    def is_chain_supported(self, chain):
        
        supported_chains = ["Ethereum", "BinanceSmartChain"]
        return chain in supported_chains

if __name__ == "__main__":
    bridge = BlockchainBridge()
    bridge.transfer_asset("Ethereum", "BinanceSmartChain", "ETH", 1, "0xReceiverAddress")