import binascii
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json

class Wallet:

        def __init__(self, address):
                self.public_key, self.private_key = generate_wallet()
                self.address = address
                self.transactions = []

        #def balance():
               
def generate_wallet():
        random_gen = Crypto.Random.new().read
        private_key = RSA.generate(1024, random_gen)
        public_key = private_key.publickey()
        private_key = str(binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'))
        public_key = str(binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii'))
        return public_key, private_key
