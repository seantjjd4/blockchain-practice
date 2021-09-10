import time
import hashlib
import rsa
import socket
import sys
import threading
import pickle

class Transaction:
    def __init__(self, sender, receiver, amount, fee, message):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.fee = fee
        self.message = message

def initialize_transaction(sender, receiver, amount, fee, message):
    # No need to check balance
    new_transaction = Transaction(sender, receiver, amount, fee, message)
    return new_transaction

def transaction_to_string(self, transaction):
        transaction_dict = {
            'sender': str(transaction.sender),
            'receiver': str(transaction.receiver),
            'amount': transaction.amount,
            'fee': transaction.fee,
            'message': transaction.message
        }
        return str(transaction_dict)

def sign_transaction(self, transaction, private):
    private_key = '-----BEGIN RSA PRIVATE KEY-----\n'
    private_key += private
    private_key += '\n-----END RSA PRIVATE KEY-----\n'
    private_key_pkcs = rsa.PrivateKey.load_pkcs1(private_key.encode('utf-8'))
    transaction_str = self.transaction_to_string(transaction)
    signature = rsa.sign(transaction_str.encode('utf-8'), private_key_pkcs, 'SHA-1')
    return signature

def handle_receive():
    while True:
        response = client.recv(4096)
        if response:
            print(f"[*] Message from node: {response}")

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

if __name__ == "__main__":
    target_host = "127.0.0.1"
    target_port = int(sys.argv[1])
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((target_host, target_port))

    receive_handler = threading.Thread(target=handle_receive, args=())
    receive_handler.start()

    command_dict = {
        "1": "generate_address",
        "2": "get_balance",
        "3": "transaction"
    }

    while True:
        print("Command list:")
        print("1. generate_address")
        print("2. get_balance")
        print("3. transaction")
        command = input("Command: ")
        if str(command) not in command_dict.keys():
            print("Unknown command.")
            continue
        message = {
            "request": command_dict[str(command)]
        }
        if command_dict[str(command)] == "generate_address":
            address, private_key = generate_address()
            print(f"Address: {address}")
            print(f"Private key: {private_key}")
        elif command_dict[str(command)] == "get_balance":
            address = input("Address: ")
            message['address'] = address
            client.send(pickle.dumps(message))
        elif command_dict[str(command)] == "transaction":
            message['address'] = input("Address: ")
            private_key = input("Private_key: ")
            message['receiver'] = input("Receiver: ")
            message['amount'] = input("Amount: ")
            message['fee'] = input("Fee: ")
            message['comment'] = input("Comment: ")
            new_transaction = initialize_transaction(
                message["address"],
                message["receiver"],
                int(message["amount"]),
                int(message["fee"]),
                message["comment"]
            )
            signature = sign_transaction(new_transaction, private_key)
            message["signature"] = signature
            client.send(str(message).encode('utf8'))
        else:
            print("Unknown command.")
            time.sleep(1)