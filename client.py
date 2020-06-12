import os
import socket
import json

import time
import transaction
import wallet
#import node

s = None
myip = ''
ips = []
ports = []
ids = []
keys = []

def check_and_read_file():
    global ips, ports, ids, keys
    
    while (os.path.exists('ip-port.txt') == False):
        pass
    while (os.stat('ip-port.txt').st_size == 0):
        pass
    with open('ip-port.txt', 'r') as file:
        for line in file:
            line = line.strip('\n')
            line = line.split(',')
            ips.append(line[0])
            ports.append(int(line[1]))
            ids.append(int(line[2]))
            keys.append(line[3])
            if (line[0] == myip):
                myid = int(line[2])
    os.remove('ip-port.txt')

def create_transaction_broadcast(sender_address, sender_private_key, recipient_address, value):
    global ips, ports, ids, keys

    transaction_val = transaction.Transaction(sender_address, sender_private_key, recipient_address, value)
    response = {'transaction': transaction_val.to_dict(), 'signature': transaction_val.sign_transaction()}
    message = json.dumps(response)
                
    for i in range(0,len(ips)):
        t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        t.connect((ips[i], ports[i]))                        
        t.send(message.encode('ascii'))
        t.close()
        
def Main():
    global ips, ports, ids, keys, connections
    
    myip = socket.gethostbyname(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '192.168.1.6'
    port = 12345
    s.connect((host, port))

    mywallet = wallet.Wallet(myip)
    message = mywallet.public_key
    s.send(message.encode('ascii'))
    s.close()
    
    check_and_read_file()

    for i in range(0,len(ips)):
        if (myip == ips[i]):
            myid = ids[i]
            break

    if (myid == 0):
        for i in range(1,len(ips)):
            create_transaction_broadcast(keys[0], mywallet.private_key, keys[i], 100)
    
    max_ammount = 100*len(ips)

    path = os.getcwd()
    with open(path+'/transactions/5nodes/transactions0.txt', 'r') as f:
        for line in f:
            if ('id1' in line or 'id0' in line):

                line = (line.strip('\n')).split(' ')
                recipient_id = int((line[0])[2])
                ammount = int(line[1])
                if (ammount <= max_ammount):
                    if recipient_id in ids:
                        create_transaction_broadcast(keys[myid], mywallet.private_key, keys[recipient_id], ammount)
                    else:
                        print('Invalid {} id'.format(recipient_id))
                else:
                    print('Ammount exceeds the maximum possible ammount to transfer')
    f.close()
        
if __name__ == '__main__':
    Main()
