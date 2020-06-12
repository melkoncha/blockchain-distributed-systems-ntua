import binascii
import json
from collections import OrderedDict

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import json
import hashlib


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):

        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.receiver_address = recipient_address
        self.amount = value
        self.transaction_id = self.transactionHash()  

    def transactionHash(self):
        string = (str(self.sender_address)+str(self.sender_private_key)+str(self.receiver_address)+str(self.amount)).encode()
        return hashlib.sha256(string).hexdigest()
    
    def to_dict(self):
        return OrderedDict({'transaction_id': self.transaction_id,
                            'sender_address': self.sender_address,
                            'recipient_address': self.receiver_address,
                            'value': self.amount})

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        sign_val = PKCS1_v1_5.new(private_key)
        hash_val = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(sign_val.sign(hash_val)).decode('ascii')

       
