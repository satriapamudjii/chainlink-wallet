from flask import Flask, request, jsonify
from web3 import Web3
from pytezos import pytezos
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

app = Flask(__name__)

ethereum_node_url = os.getenv('ETH_NODE_URL')
web3_ethereum = Web3(Web3.HTTPProvider(ethereum_node_url))

tezos_node_url = os.getenv('TEZOS_NODE_URL')
pytezos_client = pytezos.using(shell=tezos_node_url)

@lru_cache(maxsize=512)
def fetch_ethereum_wallet_balance(address):
    balance = web3_ethereum.eth.get_balance(address)
    return web3_ethereum.fromWei(balance, 'ether')

@app.route('/balance/ethereum/<address>', methods=['GET'])
def display_ethereum_balance(address):
    try:
        ether_balance = fetch_ethereum_wallet_balance(address)
        return jsonify({'address': address, 'balance': str(ether_balance), 'currency': 'ETH'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@lru_cache(maxsize=512)
def fetch_tezos_wallet_balance(address):
    return pytezos_client.contract(address).balance() / 10**6  

@app.route('/balance/tezos/<address>', methods=['GET'])
def display_tezos_balance(address):
    try:
        tez_balance = fetch_tezos_wallet_balance(address)
        return jsonify({'address': address, 'balance': str(tez_balance), 'currency': 'XTZ'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/transfer/ethereum', methods=['POST'])
def execute_ethereum_transfer():
    try:
        transaction_details = request.get_json()
        nonce = web3_ethereum.eth.getTransactionCount(transaction_details['from_address'])
        eth_transaction = {
            'nonce': nonce,
            'to': transaction_details['to_address'],
            'value': web3_ethereum.toWei(transaction_details['amount'], 'ether'),
            'gas': 21000,  # Standard gas limit
            'gasPrice': web3_ethereum.toWei('50', 'gwei'),
        }
        signed_eth_transaction = web3_ethereum.eth.account.signTransaction(eth_transaction, transaction_details['private_key'])
        transaction_hash = web3_ethereum.eth.sendRawTransaction(signed_eth_transaction.rawTransaction)
        fetch_ethereum_wallet_balance.cache_clear()
        return jsonify({'transaction_hash': web3_ethereum.toHex(transaction_hash)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/transfer/tezos', methods=['POST'])
def execute_tezos_transfer():
    try:
        transfer_details = request.get_json()
        operation_group = pytezos_client.transaction(destination=transfer_details['to_address'], amount=transfer_details['amount']).autofill().sign().inject(_async=False)
        fetch_tezos_wallet_balance.cache_clear()
        return jsonify({'operation_group_hash': operation_group['hash']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)