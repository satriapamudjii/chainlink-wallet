from flask import Flask, request, jsonify
from web3 import Web3
from pytezos import pytezos
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

app = Flask(__name__)

eth_node_url = os.getenv('ETH_NODE_URL')
web3 = Web3(Web3.HTTPProvider(eth_node_url))

tezos_node_url = os.getenv('TEZOS_NODE_URL')
pytezos_client = pytezos.using(shell=tezos_node_url)

@lru_cache(maxsize=512)
def get_ethereum_balance_internal(address):
    balance = web3.eth.get_balance(address)
    return web3.fromWei(balance, 'ether')

@app.route('/balance/ethereum/<address>', methods=['GET'])
def get_ethereum_balance(address):
    try:
        ether = get_ethereum_balance_internal(address)
        return jsonify({'address': address, 'balance': str(ether), 'currency': 'ETH'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@lru_cache(maxsize=512)
def get_tezos_balance_internal(address):
    return pytezos_client.contract(address).balance() / 10**6  

@app.route('/balance/tezos/<address>', methods=['GET'])
def get_tezos_balance(address):
    try:
        tez = get_tezos_balance_internal(address)
        return jsonify({'address': address, 'balance': str(tez), 'currency': 'XTZ'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/transfer/ethereum', methods=['POST'])
def transfer_ethereum():
    try:
        data = request.get_json()
        nonce = web3.eth.getTransactionCount(data['from_address'])
        tx = {
            'nonce': nonce,
            'to': data['to_address'],
            'value': web3.toWei(data['amount'], 'ether'),
            'gas': 21000,  
            'gasPrice': web3.toWei('50', 'gwei'),
        }
        signed_tx = web3.eth.account.signTransaction(tx, data['private_key'])
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        get_ethereum_balance_internal.cache_clear()
        return jsonify({'transaction_hash': web3.toHex(tx_hash)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/transfer/tezos', methods=['POST'])
def transfer_tezos():
    try:
        data = request.get_json()
        opg = pytezos_client.transaction(destination=data['to_address'], amount=data['amount']).autofill().sign().inject(_async=False)
        get_tezos_balance_internal.cache_clear()
        return jsonify({'operation_group_hash': opg['hash']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)