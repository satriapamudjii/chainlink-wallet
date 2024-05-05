import os
import json
import hashlib
from ecdsa import SigningKey, NIST384p
from dotenv import load_dotenv

load_dotenv()

class SecurityManager:
    def __init__(self):
        self.private_key_path = os.getenv("PRIVATE_KEY_PATH", "private_key.pem")

    def load_private_key(self):
        try:
            with open(self.private_key_path) as f:
                sk = SigningKey.from_pem(f.read())
            return sk
        except FileNotFoundError:
            raise FileNotFoundError("Private key file not found.")
    
    @staticmethod
    def validate_input(transaction):
        if not isinstance(transaction, dict):
            raise ValueError("Transaction must be a dictionary.")
        
        required_keys = {"from", "to", "amount"}
        if not required_keys.issubset(transaction.keys()):
            raise ValueError("Transaction dictionary misses required keys.")
        if not isinstance(transaction["amount"], (int, float)) or transaction["amount"] <= 0:
            raise ValueError("Transaction amount is invalid.")
    
    @staticmethod
    def generate_transaction_hash(transaction):
        transaction_str = json.dumps(transaction, sort_keys=True)
        return hashlib.sha256(transaction_str.encode('utf-8')).hexdigest()
    
    def sign_transaction(self, transaction):
        self.validate_input(transaction)
        
        transaction_hash = self.generate_transaction_hash(transaction)
        private_key = self.load_private_key()
        
        signature = private_key.sign(transaction_hash.encode('utf-8'))
        return signature.hex()

    @staticmethod
    def verify_signature(transaction, signature, public_key):
        transaction_hash = SecurityManager.generate_transaction_hash(transaction)
        
        try:
            vk = SigningKey.from_pem(public_key).verifying_key
            return vk.verify(bytes.fromhex(signature), transaction_hash.encode('utf-8'))
        except Exception:
            return False

if __name__ == "__main__":
    transaction = {"from": "Alice", "to": "Bob", "amount": 10}
    public_key_path = "public_key.pem"

    sec_manager = SecurityManager()
    signature = sec_manager.sign_transaction(transaction)

    with open(public_key_path) as f:
        public_key = f.read()

    is_verified = SecurityManager.verify_signature(transaction, signature, public_key)
    print(f"Transaction Verified: {is_verified}")