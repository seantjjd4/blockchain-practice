import time
import hashlib
import rsa


class Transaction:
    def __init__(self, sender, receiver, amount, fee, message):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.fee = fee
        self.message = message

class Block:
    def __init__(self, previous_hash, difficulty, miner, miner_rewards):
        self.previous_hash = previous_hash
        self.hash = ''
        self.difficulty = difficulty
        self.nonce = 0
        self.timestamp = int(time.time())
        self.transactions = []
        self.miner = miner
        self.miner_rewards = miner_rewards

class BlockChain:
    def __init__(self):
        self.adjust_difficulty_blocks = 100
        self.difficulty = 5
        self.block_time = 15
        self.miner_rewards = 50
        self.block_limitation = 10
        self.chain = []
        self.pending_transactions = []

    def transaction_to_string(self, transaction):
        transaction_dict = {
            'sender': str(transaction.sender),
            'receiver': str(transaction.receiver),
            'amount': transaction.amount,
            'fee': transaction.fee,
            'message': transaction.message
        }
        return str(transaction_dict)

    def get_transaction_string(self, block):
        transaction_str = ''
        for transaction in block.transactions:
            transaction_str += self.transaction_to_string(transaction)
        return transaction_str
    
    def get_hash(self, block, nonce):
        s = hashlib.sha1()
        s.update(
            (
                block.previous_hash + str(block.timestamp) + self.get_transaction_string(block) + str(nonce)
            ).encode("utf-8")
        )
        h = s.hexdigest()
        return h
    
    def add_transaction_to_block(self, block):
        self.pending_transactions.sort(key=lambda x: x.fee, reverse=True)

        if len(self.pending_transactions) > self.block_limitation:
            transaction_accepted = self.pending_transactions[:self.block_limitation]
            self.pending_transactions = self.pending_transactions[self.block_limitation:]
        else:
            transaction_accepted = self.pending_transactions
            self.pending_transactions = []
        block.transactions = transaction_accepted

    def create_genesis_block(self):
        print("Create genesis block")
        new_block = Block("Made by tjjd4", self.difficulty, 'tjjd4', self.miner_rewards)
        new_block.hash = self.get_hash(new_block, 0)
        self.chain.append(new_block)

    def mine_block(self, miner):
        start_time = time.process_time()
        last_block = self.chain[-1]
        new_block = Block(last_block.hash, self.difficulty, miner, self.miner_rewards)

        self.add_transaction_to_block(new_block)
        new_block.previous_hash = last_block.hash
        new_block.difficulty = self.difficulty
        new_block.hash = self.get_hash(new_block, new_block.nonce)

        while new_block.hash[0:self.difficulty] != '0' *self.difficulty:
            new_block.nonce += 1
            new_block.hash = self.get_hash(new_block, new_block.nonce)

        time_consumed = round(time.process_time() - start_time, 5)
        print(f"Hash found: {new_block.hash} @ difficutly {self.difficulty}, time cost: {time_consumed}s")
        self.chain.append(new_block)

    def adjust_difficulty(self):
        if len(self.chain) % self.adjust_difficulty_blocks != 0:
            return self.difficulty
        elif len(self.chain) <= self.adjust_difficulty_blocks:
            return self.difficulty
        else:
            start = self.chain[-1*self.adjust_difficulty_blocks-1].timestamp
            finish = self.chain[-1].timestamp
            average_time_consumed = round((finish - start) / (self.adjust_difficulty_blocks), 2)
            if average_time_consumed > self.block_time:
                print(f"Average block time: {average_time_consumed}s. Lower the difficulty")
                self.difficulty -= 1
            else:
                print(f"Average block time: {average_time_consumed}s. High up the difficulty")
                self.difficulty += 1

    def get_balance(self, account):
        balance = 0
        for block in self.chain:
            miner = False
            if block.miner == account:
                miner = True
                balance += self.miner_rewards
            
            for transaction in block.transactions:
                if miner:
                    balance += transaction.fee
                if transaction.sender == account:
                    balance -= transaction.fee
                    balance -= transaction.amount
                elif transaction.receiver == account:
                    balance += transaction.amount
        return balance

    def verify_blockchain(self):
        previous_hash = ''
        for idx, block in enumerate(self.chain):
            if self.get_hash(block, block.nonce) != block.hash:
                print("Error: hash doesn't matched")
                return False
            elif previous_hash != block.previous_hash and idx:
                print("Error: Hash doesn't matched to the previous_hash")
            previous_hash = block.hash
        print("Hash correct, chain hasn't been changed")
        return True

    def generate_address(self):
        public, private = rsa.newkeys(512)
        public_key = public.save_pkcs1()
        private_key = private.save_pkcs1()
        return self.get_address_from_public(public_key), self.extract_from_private(private_key)

    def get_address_from_public(self, public):
        address = str(public).replace('\\n', '')
        address = address.replace("b'-----BEGIN RSA PUBLIC KEY-----", '')
        address = address.replace("-----END RSA PUBLIC KEY-----", '')
        print("Address: ", address)
        return address

    def extract_from_private(self, private):
        private_key = str(private).replace('\\n', '')
        private_key = private_key.replace("b'-----BEGIN RSA PRIVATE KEY-----", '')
        private_key = private_key.replace("-----END RSA PRIVATE KEY-----", '')
        return private_key

    def add_transaction(self, transaction, signature):
        public_key = '-----BEGIN RSA PUBLIC KEY-----\n'
        public_key += transaction.sender
        public_key += '\n-----END RSA PUBLIC KEY-----\n'
        public_key_pkcs = rsa.PublicKey.load_pkcs1(public_key.encode('utf-8'))
        transaction_str = self.transaction_to_string(transaction)

        if transaction.fee + transaction.amount > self.get_balance(transaction.sender):
            return False, "Balance is not enough!"
        try:
            rsa.verify(transaction_str.encode('utf-8'), signature, public_key_pkcs)
            self.pending_transactions.append(transaction)
            return True, "Authorized successfully"
        except Exception:
            return False, "RSA verify wrong"

    def initialize_transaction(self, sender, receiver, amount, fee, message):
        if self.get_balance(sender) < amount + fee:
            print("Balance is not enough!")
            return False
        new_transaction = Transaction(sender, receiver, amount, fee, message)
        return new_transaction
    
    def sign_transaction(self, transaction, private):
        private_key = '-----BEGIN RSA PRIVATE KEY-----\n'
        private_key += private
        private_key += '\n-----END RSA PRIVATE KEY-----\n'
        private_key_pkcs = rsa.PrivateKey.load_pkcs1(private_key.encode('utf-8'))
        transaction_str = self.transaction_to_string(transaction)
        signature = rsa.sign(transaction_str.encode('utf-8'), private_key_pkcs, 'SHA-1')
        return signature

    def start(self):
        address, private = self.generate_address()
        self.create_genesis_block()
        while (True):
        # Step1: initialize a transaction
            transaction = self.initialize_transaction(address, 'test123', 1, 1, 'Test')
            if transaction:
                # Step2: Sign your transaction
                signature = self.sign_transaction(transaction, private)
            # Step3: Send it to blockchain
                self.add_transaction(transaction, signature)
            self.mine_block(address)
            print(self.get_balance(address))
            self.adjust_difficulty()

    

    

if __name__ == '__main__':
    block = BlockChain()
    block.start()
    """
    block = BlockChain()
    block.create_genesis_block()
    block.mine_block('tjjd4')
    block.verify_blockchain()
    print("Insert fake transaction.")
    fake_transaction = Transaction('test123', 'address', 100, 1, 'Test')
    block.chain[1].transactions.append(fake_transaction)
    block.mine_block('tjjd4')
    block.verify_blockchain()
    """