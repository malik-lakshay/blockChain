from flask import Flask, jsonify, request
import hashlib
import json

app = Flask(__name__)


class Transaction:
    def __init__(self, sender, receiver, amount, transactionID):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.transactionID = transactionID

    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'transactionID': self.transactionID
        }


class Block:
    def __init__(self, transactions, prev_hash):
        self.transactions = transactions[:5]  # Take only the first 2 transactions
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        transactions_json = json.dumps([tx.__dict__ for tx in self.transactions], sort_keys=True)
        block_content = str(self.prev_hash) + transactions_json
        return hashlib.sha256(block_content.encode()).hexdigest()


class MyBlockchain:
    def __init__(self):
        hashLast = self.hashgenerator('last_gen')
        hashFirst = self.hashgenerator('first_gen')
        genesis_transaction = Transaction("Genesis", "Genesis", 0, "TransactionID")
        genesis = Block([genesis_transaction], hashLast)
        self.chain = [genesis]

    def hashgenerator(self, data):
        result = hashlib.sha256(data.encode())
        return result.hexdigest()

    def addBlock(self, transactions):
        prev_hash = self.chain[-1].hash
        tx_objects = [Transaction(tx['sender'], tx['receiver'], tx['amount'], tx['transactionID']) for tx in transactions]
        if len(tx_objects) <= 5:
            block = Block(tx_objects, prev_hash)
            self.chain.append(block)
        else:
            while tx_objects:
                block_transactions = tx_objects[:5]
                block = Block(block_transactions, prev_hash)
                self.chain.append(block)
                tx_objects = tx_objects[5:]
                prev_hash = block.hash

    def traverseBlockchain(self):
        for block in self.chain:
            print("Transactions:")
            for tx in block.transactions:
                print("  Sender:", tx.sender)
                print("  Receiver:", tx.receiver)
                print("  Amount:", tx.amount)
            print("Hash:", block.hash)
            print("Previous Hash:", block.prev_hash)
            print("=" * 30)


blockchain = MyBlockchain()


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    transactions = data.get('transactions')
    blockchain.addBlock(transactions)
    return jsonify({'message': 'Transaction added to the blockchain'})


@app.route('/get_chain', methods=['GET'])
def get_chain():
    chain = []
    for block in blockchain.chain:
        transactions = [t.__dict__ for t in block.transactions]  # Convert Transaction objects to dictionaries
        block_data = {'transactions': transactions, 'hash': block.hash, 'previous_hash': block.prev_hash}
        chain.append(block_data)
    return jsonify({'chain': chain})


@app.route('/get_last_block', methods=['GET'])
def get_last_block():
    last_block = blockchain.chain[-1]
    last_block_dict = {
        'transactions': [tx.to_dict() for tx in last_block.transactions],
        'prev_hash': last_block.prev_hash,
        'hash': last_block.hash
    }
    return jsonify({'last_block': last_block_dict})


@app.route('/hello')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run()
