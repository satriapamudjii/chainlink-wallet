import os
import json
import hashlib
from base64 import b64encode, b64decode
from ecdsa import SigningKey, VerifyingKey, BadSignatureError, NIST384p
from ecdsa.util import sigencode_der, sigdecode_der
from dotenv import load_dotenv

load_dotenv()

class WalletSecurityManager:
    def __init__(self):
        self.private_key_path = os.getenv("PRIVATE_KEY_PATH", "private_key.pem")
        self.public_key_path = os.getenv("PUBLIC_KEY_PATH", "public_key.pem")

    @staticmethod
    def create_new_blockchain_wallet(private_key_path="private_key.pem", public_key_path="public_key.pem"):
        signing_key = SigningKey.generate(curve=NIST384p)
        verifying_key = signing_key.get_verifying_key()

        with open(private_key_path, "w") as private_file:
            private_file.write(signing_key.to_pem().decode())
        
        with open(public_key_path, "w") as public_file:
            public_file.write(verifying_key.to_pem().decode())

        print(f"New wallet created with keys stored at: {private_key_path}, {public_key_path}")

    def load_signing_key(self):
        try:
            with open(self.private_key_path, 'r') as private_file:
                return SigningKey.from_pem(private_file.read())
        except FileNotFoundError:
            raise FileNotFoundError("Private key file not found. Please check the path.")
        except Exception as ex:
            raise Exception(f"Unexpected error loading private key: {ex}")

    def load_verifying_key(self):
        try:
            with open(self.public_key_path, 'r') as public_file:
                return VerifyingKey.from_pem(public_file.read())
        except FileNotFoundError:
            raise FileNotFoundError("Public key file not found. Please check the path.")
        except Exception as ex:
            raise Exception(f"Unexpected error loading public key: {ex}")

    @staticmethod
    def validate_transaction_structure(transaction):
        if not isinstance(transaction, dict):
            raise ValueError("Transaction must be a dictionary.")
        
        required_keys = {"from", "to", "amount"}
        if not required_keys.issubset(transaction.keys()):
            raise ValueError("Transaction dictionary is missing required keys: 'from', 'to', 'amount'.")
        
        if not isinstance(transaction["amount"], (int, float)) or transaction["amount"] <= 0:
            raise ValueError("Transaction amount must be a positive number.")

    @staticmethod
    def compute_transaction_hash(transaction):
        transaction_string = json.dumps(transaction, sort_keys=True)
        return hashlib.sha256(transaction_string.encode('utf-8')).hexdigest()
    
    def sign_blockchain_transaction(self, transaction):
        WalletSecurityManager.validate_transaction_structure(transaction)
        
        transaction_hash = WalletSecurityManager.compute_transaction_hash(transaction)
        signing_key = self.load_signing_key()
        
        transaction_signature = signing_key.sign(transaction_hash.encode('utf-8'), sigencode=sigencode_der)
        return b64encode(transaction_signature).decode()

    @staticmethod
    def verify_transaction_signature(transaction, signature, verifying_key_str):
        transaction_hash = WalletSecurityManager.compute_transaction_hash(transaction)
        
        try:
            verifying_key = VerifyingKey.from_pem(verifying_key_str)
            return verifying_key.verify(b64decode(signature), transaction_hash.encode('utf-8'), sigdecode=sigdecode_der)
        except BadSignatureError:
            return False
        except Exception as ex:
            raise Exception(f"Unexpected error verifying signature: {ex}")

if __name__ == "__main__":
    transaction_details = {"from": "Alice", "to": "Bob", "amount": 10}
    
    security_manager = WalletSecurityManager()
    
    if not os.path.exists(security_manager.private_key_path) or not os.path.exists(security_manager.public_key_path):
        WalletSecurityManager.create_new_blockchain_wallet(security_manager.private_key_path, security_manager.public_key_path)
    
    try:
        transaction_signature = security_manager.sign_blockchain_transaction(transaction_details)

        with open(security_manager.public_key_path, 'r') as public_file:
            public_key_str = public_file.read()
        
        signature_verification_status = WalletSecurityManager.verify_transaction_signature(transaction_details, transaction_signature, public_key_str)
        
        print(f"Transaction Verified: {signature_verification_status}")
    except Exception as ex:
        print(f"An error occurred: {ex}")