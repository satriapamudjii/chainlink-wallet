import os
import json
import hashlib
from ecdsa import SigningKey, VerifyingKey, BadSignatureError, NIST384p
from ecdsa.keys import MalformedPointError
from dotenv import load_dotenv

load_dotenv()

class SecurityManager:
    def __init__(self):
        self.private_key_path = os.getenv("PRIVATE_KEY_PATH", "private_key.pem")
        self.public_key_path = os.getenv("PUBLIC_KEY_PATH", "public_key.pem")

    @staticmethod
    def create_new_wallet(private_key_path="private_key.pem", public_key_path="public_key.pem"):
        """
        Generates a new wallet with private and public key.
        """
        sk = SigningKey.generate(curve=NIST384p)
        vk = sk.get_verifying_key()

        with open(private_key_path, "w") as f:
            f.write(sk.to_pem().decode())
        
        with open(public_key_path, "w") as f:
            f.write(vk.to_pem().decode())

        print("New wallet created with keys stored at: {}, {}".format(private_key_path, public_key_path))

    def load_private_key(self):
        """
        Loads the user's private key from the specified path.
        """
        try:
            with open(self.private_key_path, 'r') as f:
                return SigningKey.from_pem(f.read())
        except FileNotFoundError:
            raise FileNotFoundError("Private key file not found. Please check the path.")
        except Exception as e:
            raise Exception(f"Unexpected error loading private key: {e}")

    @staticmethod
    def validate_input(transaction):
        """
        Validates the input transaction format.
        """
        if not isinstance(transaction, dict):
            raise ValueError("Transaction must be a dictionary.")
        
        required_keys = {"from", "to", "amount"}
        if not required_keys.issubset(transaction.keys()):
            raise ValueError("Transaction dictionary is missing required keys: 'from', 'to', 'amount'.")
        
        if not isinstance(transaction["amount"], (int, float)) or transaction["amount"] <= 0:
            raise ValueError("Transaction amount must be a positive number.")

    @staticmethod
    def generate_transaction_hash(transaction):
        """
        Generates a SHA256 hash for the transaction.
        """
        transaction_str = json.dumps(transaction, sort_keys=True)
        return hashlib.sha256(transaction_str.encode('utf-8')).hexdigest()
    
    def sign_transaction(self, transaction):
        """
        Signs the transaction with the user's private key.
        """
        self.validate_input(transaction)
        
        transaction_hash = self.generate_transaction_hash(transaction)
        private_key = self.load_private_key()
        
        signature = private_key.sign(transaction_hash.encode('utf-8'))
        return signature.hex()

    @staticmethod
    def verify_signature(transaction, signature, public_key_str):
        """
        Verifies the transaction signature with the given public key.
        """
        transaction_hash = SecurityManager.generate_transaction_hash(transaction)
        
        try:
            vk = VerifyingKey.from_pem(public_key_str)
            return vk.verify(bytes.fromhex(signature), transaction_hash.encode('utf-8'))
        except BadSignatureError:
            return False
        except Exception as e:
            raise Exception(f"Unexpected error verifying signature: {e}")

if __name__ == "__main__":
    transaction = {"from": "Alice", "to": "Bob", "amount": 10}
    
    sec_manager = SecurityManager()
    
    # Optional: Automatically generate wallet if keys do not exist
    if not os.path.exists(sec_manager.private_key_path) or not os.path.exists(sec_manager.public_key_path):
        SecurityManager.create_new_wallet(sec_manager.private_key_path, sec_manager.public_key_path)
    
    try:
        signature = sec_manager.sign_transaction(transaction)

        with open(sec_manager.public_key_path, 'r') as f:
            public_key = f.read()
        
        is_verified = SecurityManager.verify_signature(transaction, signature, public_key)
        
        print(f"Transaction Verified: {is_verified}")
    except Exception as e:
        print(f"An error occurred: {e}")