import binascii
import json
import hashlib
import Crypto
import time
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from collections import OrderedDict

import block
import wallet
import transaction
import socket

BLOCK_CAPACITY = 5
MINING_DIFFICULTY = 4

class Node:
        
        def __init__(self, ip, port, ids, myid, publickey):
                self.ip = ip
                self.port = port
                self.publickey = publickey
                self.myid = myid
                self.id = ids
                self.NBCs = [100*len(ip)]
                for i in range(1,len(self.ip)):
                        self.NBCs.append(0)
                self.chain = []
                self.transactions = []
                if ( myid == 0 ):
                        '''
                        If bootstrap node, create the genesis block
                        '''
                        index = 0
                        nonce = 0
                        previous_hash = 1
                        tran = transaction.Transaction('0', None, self.publickey[0], self.NBCs[0])
                        self.transactions.append(tran.to_dict())
                        genesis_block = self.create_new_block(index, nonce, previous_hash, time.time())
                        genesis_block_form = {'block': genesis_block.to_dict()}
                        self.validate_block(genesis_block_form)
                        self.broadcast_block(genesis_block)
                        
        def validate_transaction(self, received):
                transaction = received['transaction']['sender_address']
                for i in range(0,len(self.ip)):
                        if (received['transaction']['sender_address'] == str(self.publickey[i])):
                                break
                for j in range(0,len(self.ip)):
                        if (received['transaction']['recipient_address'] == str(self.publickey[j])):
                                break
                sign_verification = self.verify_signature(self.publickey[i], received['signature'], received['transaction'])
                if sign_verification:
                        ammount = int(received['transaction']['value'])
                        print(i,j,ammount)
                        if (ammount <= self.NBCs[i]):
                                self.NBCs[i] -= ammount
                                self.NBCs[j] += ammount
                                self.transactions.append(received['transaction'])
                                if (i == self.myid or j == self.myid):
                                        print("My wallet's balance is {}".format(self.NBCs[self.myid]))
                                if (len(self.transactions) == BLOCK_CAPACITY):
                                     block = self.mine_block()
                                     self.broadcast_block(block)
                                     block_form = {'block': block.to_dict()}
                                     valid = self.validate_block(block_form)
                                     if valid:
                                             return True
                                     else:
                                             return False
                        else:
                                print('Not enough ammount')
                                return False
                else:
                         print('Sign verification failed')
                         return False
           
        def verify_signature(self, sender_key, signature, transaction):
                public_key = RSA.importKey(binascii.unhexlify(sender_key))
                verifier = PKCS1_v1_5.new(public_key)
                h = SHA.new(str(transaction).encode('utf8'))
                return verifier.verify(h, binascii.unhexlify(signature))

        def mine_block(self):
                nonce, previous_hash, timestamp = self.proof_of_work()
                index = len(self.chain)
                block = self.create_new_block(index, nonce, previous_hash, float(timestamp))
                return block

        def proof_of_work(self):
                previous_block = self.chain[-1]
                previous_hash = previous_block.current_hash
                nonce = 0
                timestamp = time.time()
                while self.valid_proof(len(self.chain), timestamp, self.transactions, previous_hash, nonce) is False:
                        nonce += 1
                        timestamp = time.time()
                return nonce, previous_hash, timestamp
        
        def valid_proof(self, index, timestamp, transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
                val = (str(index)+str(last_hash)+str(timestamp)+str(transactions)+str(nonce)).encode()
                val_hash = hashlib.sha256(val).hexdigest()
                return val_hash[:difficulty] == '0'*difficulty

        def create_new_block(self, index, nonce, previous_hash, timestamp):
                block_val = block.Block(index, nonce, previous_hash, self.transactions, timestamp)
                setattr(block_val, 'current_hash', block_val.myHash(MINING_DIFFICULTY))
                self.transactions = []
                return block_val

        def broadcast_block(self, block):
                message = {'block': block.to_dict()}
                to_broadcast = json.dumps(message)

                for i in range(0,len(self.ip)):
                        if (i != self.myid):
                                t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                t.connect((self.ip[i], int(self.port[i])))                        
                                t.send(to_broadcast.encode('ascii'))
                                t.close()

        def validate_block(self, received):
                index = int(received['block']['index'])
                previous_hash = received['block']['previous_hash']
                timestamp = received['block']['timestamp']
                transactions = received['block']['transactions']
                nonce = int(received['block']['nonce'])
                current_hash = received['block']['current_hash']
                recv_block = block.Block(index, nonce, previous_hash, transactions, timestamp)
                if (index != 0):
                        if (index > len(self.chain) - 1):
                                if (str(recv_block.myHash(MINING_DIFFICULTY)) == current_hash):
                                        last_block = self.chain[-1]
                                        last_hash = str(last_block.current_hash)
                                        if (previous_hash == last_hash):
                                                print('Block with index {} is validated'.format(index))
                                                setattr(recv_block, 'current_hash', current_hash)
                                                self.chain.append(recv_block)
                                                print(recv_block.listOfTransactions)
                                                #attrs = vars(recv_block)
                                                #print(', '.join("%s: %s" % item for item in attrs.items()))
                                                return True
                                        else:
                                                print('Invalid previous hash. Index {}'.format(index))
                                                return False
                                else:
                                        print('Invalid current hash. Index {}'.format(index))
                                        return False
                        else:
                                print('Block with index {} has already been inserted'.format(index))
                else:
                        setattr(recv_block, 'current_hash', current_hash)
                        self.chain.append(recv_block)
                        print('Genesis block appended')
                        print(recv_block.listOfTransactions)
                        #attrs = vars(recv_block)
                        #print(', '.join("%s: %s" % item for item in attrs.items()))
                        return True

        def valid_chain(self, chain):
                previous_block = chain[0]
                '''
                index = int(previous_block['index'])
                previous_hash = previous_block['previous_hash']
                timestamp = previous_block['timestamp']
                transactions = previous_block['transactions']
                nonce = int(previous_block['nonce'])
                current_hash = previous_block['current_hash']
                previous_block = block.Block(index, nonce, previous_hash, transactions, timestamp)
                '''
                current_index = 1

                while (current_index < len(chain)):
                        cur_block = chain[current_index]
                        '''
                        index = int(block['index'])
                        previous_hash = block['previous_hash']
                        timestamp = block['timestamp']
                        transactions = block['transactions']
                        nonce = int(block['nonce'])
                        current_hash = block['current_hash']
                        cur_block = block.Block(index, nonce, previous_hash, transactions, timestamp)
                        '''
                        
                        if (cur_block.previous_hash != str(previous_block.myHash())):
                                return False

                        previous_block = cur_block
                        current_index += 1
                return True

        def resolve_conflicts(self, response):
                new_chain = response['chain']
                length = int(response['length'])
                max_length = len(self.chain)

                if ((length > max_length) and self.valid_chain(new_chain)):
                        self.chain = new_chain
                        return True
                else:
                        return False
