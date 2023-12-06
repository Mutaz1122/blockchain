import sys
import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
import requests
from urllib.parse import urlparse
from flask_cors import CORS


class Blockchain(object):
    difficulty_target = "0000"
    
    def hash_block(self, block):
        block_encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_encoded).hexdigest()
    
    def __init__(self, node_identifier):
        self.nodes = set()
        self.chain = []
        self.current_transactions = []
        self.utxo_set = {}  # New: UTXO set to track unspent coins

        genesis_hash = self.hash_block("genesis_block")
        self.append_block(
            hash_of_previous_block=genesis_hash,
            nonce=self.proof_of_work(0, genesis_hash, [])
        )
        transaction = {
            'amount': 10,
            'recipient': node_identifier,
            'sender':"gift"
        }

            
        self.current_transactions.append(transaction)
        
    def proof_of_work(self, index, hash_of_previous_block, transactions):
        nonce = 0
        while self.valid_proof(index, hash_of_previous_block, transactions, nonce) is False:
            nonce += 1
        return nonce
    
    def valid_proof(self, index, hash_of_previous_block, transactions, nonce):
        content = f'{index}{hash_of_previous_block}{transactions}{nonce}'.encode()
        content_hash = hashlib.sha256(content).hexdigest()
        return content_hash[:len(self.difficulty_target)] == self.difficulty_target
    
    def append_block(self, nonce, hash_of_previous_block):
        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'transactions': self.current_transactions,
            'nonce': nonce,
            'hash_of_previous_block': hash_of_previous_block
        }
        self.current_transactions = []
        self.chain.append(block)
        return block
    
    def add_transaction(self, sender, recipient, amount):

        #Double Spending issue
        current_transactions_amount = 0
        if len(self.current_transactions) > 0:
            for i in self.current_transactions:
                current_transactions_amount = current_transactions_amount + i["amount"]


        if sender == recipient and self.get_balance(sender) < (amount + current_transactions_amount):
            return False  # Insufficient funds

        transaction = {
            'amount': amount,
            'recipient': recipient,
            'sender': sender,
        }

            
        self.current_transactions.append(transaction)


        return self.last_block['index'] + 1
    
    def update_utxo_set_from_blockchain(self):
        for block in self.chain:
            transactions = block['transactions']
            for transaction in transactions:
                sender = transaction['sender']
                recipient = transaction['recipient']
                amount = transaction['amount']

                if sender != "0":
                    self.remove_from_utxo_set(sender, amount)
                    self.add_to_utxo_set(recipient, amount)
                if sender == "0":
                    self.add_to_utxo_set(recipient, amount)
                    print("added")

    def add_to_utxo_set(self, recipient, amount):
        if recipient not in self.utxo_set:
            self.utxo_set[recipient] = []
        x=0
        for utxo in self.utxo_set[recipient]:
            if utxo['transaction_id'] == self.last_block['index']:
                x=1
        if x!=1 :
            self.utxo_set[recipient].append({
                'amount': amount,
             'transaction_id': self.last_block['index'],
            })

    def remove_from_utxo_set(self, sender, amount):
        if sender in self.utxo_set:
        # Remove the UTXO associated with the spent amount
            
            print("before%s"%self.get_balance(sender))

            items_to_remove = []

            for utxo in self.utxo_set[sender]:
                if utxo['amount'] <= amount:
                    items_to_remove.append(utxo)
                    amount -= utxo['amount']
                else:
                    utxo['amount'] -= amount
                    amount = 0

                if amount == 0:
                    break

        # Remove the items after the iteration
            for item in items_to_remove:
                self.utxo_set[sender].remove(item)

    
    # def get_balance(self, address):
    #     balance = 0
    #     if address in self.utxo_set:
    #     	for utxo in self.utxo_set[address]:
    #                 balance += utxo['amount']
    #     return balance
    
    def getBalance(self, blockchain, node_address):
        
        balance = 0

        for block in blockchain:
            print(block["transactions"])

            for transaction in block["transactions"]:
                print(transaction)
                if len(transaction) == 0:
                    print(transaction)

                else:
                    
                    if transaction["sender"] == node_address:
                        balance -= transaction["amount"]
                    if transaction["recipient"] == node_address:
                        balance += transaction["amount"]

        return balance

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            if block['hash_of_previous_block'] != self.hash_block(last_block):
                return False

            if not self.valid_proof(current_index, block['hash_of_previous_block'], block['transactions'], block['nonce']):
                return False

            last_block = block
            current_index += 1

        return True

    def update_blockchain(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get(f'http://{node}/blockchain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False

    @property
    def last_block(self):
        return self.chain[-1]

app = Flask(__name__)
CORS(app)

node_identifier = str(uuid4()).replace('-', "")
blockchain = Blockchain(node_identifier)

@app.route('/blockchain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine_block():
    blockchain.add_transaction(
        sender="Mine",
        recipient=node_identifier,
        amount=1,
    )
    last_block_hash = blockchain.hash_block(blockchain.last_block)
    index = len(blockchain.chain)
    nonce = blockchain.proof_of_work(index, last_block_hash, blockchain.current_transactions)
    block = blockchain.append_block(nonce, last_block_hash)
    response = {
        'message': "New Block Mined",
        'index': block['index'],
        'hash_of_previous_block': block['hash_of_previous_block'],
        'nonce': block['nonce'],
        'transactions': block['transactions'],
    }
    blockchain.update_utxo_set_from_blockchain()
    return jsonify(response), 200

@app.route('/address', methods=['GET'])
def getAddress():
    return node_identifier, 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required_fields = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required_fields):
        return ('Missing fields', 400)

    success = blockchain.add_transaction(
        values['sender'],
        values['recipient'],
        values['amount']
    )

    if success is False:
        return jsonify({'message': 'Transaction failed. Insufficient funds.'}), 400

    response = {'message': f'Transaction will be added to Block {blockchain.last_block["index"]}'}
    return jsonify(response), 201

@app.route('/nodes/add_nodes', methods=['POST'])
def add_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Missing node(s) info", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
        'message': 'New nodes added',
        'nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/sync', methods=['GET'])
def sync():
    updated = blockchain.update_blockchain()
    if updated:
        response = {
            'message': 'The blockchain has been updated to the latest',
            'blockchain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our blockchain is the latest',
            'blockchain': blockchain.chain
        }
    blockchain.update_utxo_set_from_blockchain()
    return jsonify(response), 200


@app.route('/balance', methods=['POST'])
def balance():
    value = request.get_json()
    
    balance = blockchain.getBalance(blockchain.chain,node_identifier)
    return jsonify(balance), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(sys.argv[1]))