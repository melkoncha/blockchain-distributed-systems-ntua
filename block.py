import time
import json
from collections import OrderedDict
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
import hashlib


class Block:
        def __init__(self, index, nonce, previous_hash, transactions, timestamp):
                self.index = index
                self.previous_hash = previous_hash
                self.timestamp = timestamp
                self.listOfTransactions = transactions
                self.nonce = nonce
        
        def myHash(self, difficulty):
                string = (str(self.index)+str(self.previous_hash)+str(self.timestamp)+str(self.listOfTransactions)+str(self.nonce)).encode()
                return hashlib.sha256(string).hexdigest()

        def to_dict(self):
                return OrderedDict({'index': self.index,
                            'previous_hash': self.previous_hash,
                            'timestamp': self.timestamp,
                            'transactions': self.listOfTransactions,
                            'nonce': self.nonce,
                            'current_hash': self.current_hash})
