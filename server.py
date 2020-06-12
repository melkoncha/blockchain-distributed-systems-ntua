import subprocess
import socket
import json
from collections import OrderedDict

import node
import block

is_bootstrap = ''
nodes = 0
worksasbootstrap = False
gotallnodes = False
ips = []
ports = []
ids = []
keys = []
    
def broadcast():
    global ips, ports, ids, keys
    
    msg = ''
    for i in range(0,len(ips)):
        msg += ips[i]+','+str(ports[i])+','+str(ids[i])+','+keys[i]+'-'
    msg = msg[:-1]
    
    for i in range(1,len(ips)):
        t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        t.connect((ips[i], ports[i]))
        t.send(msg.encode('ascii'))
        t.close()

def writetofile():
    global ips, ports, ids, keys
    
    to_wr = ''
    for i in range(0,len(ips)):
        to_wr = to_wr+ips[i]+','+str(ports[i])+','+str(ids[i])+','+keys[i]+'\n'
    with open('ip-port.txt', 'w') as file:
        file.write(to_wr)
    file.close()

def request_chain(myid):
    global ips,ports

    msg = 'Update'
    for i in range(0,len(ips)):
        if (i != myid):
            t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            t.connect((ips[i], ports[i]))
            t.send(msg.encode('ascii'))
            t.close()

def Main():
    global ips, ports, ids, keys, worksasbootstrap
    
    is_bootstrap = input('Is this server bootstrap? (y/n)\n')
    if (is_bootstrap == 'y'):
        worksasbootstrap = True
        nodes = int(input('How many nodes are in the network?\n'))
    
    host = socket.gethostbyname(socket.gethostname())
    port = 12345
    print('Server IP and Port: '+host+' - '+str(port))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(100)
    print('Server is listening')
    
    #client = subprocess.Popen(['python', 'client.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)

    if worksasbootstrap:
        id = 0
        myid = 0
        
        while True:
            c, addr = s.accept()

            if (nodes > 0):
                ips.append(addr[0])
                ports.append(12345)
                ids.append(id)
                keys.append((c.recv(1024)).decode('ascii'))
                c.close()
                
                id +=1
                nodes -= 1
                
                if (nodes == 0):
                    print('All nodes have been inserted in network. Broadcasting their connection values.')
                    writetofile()
                    broadcast()
                    break
    else:
        c, addr = s.accept()
        data = (c.recv(2048)).decode('ascii')
        data = data.split('-')
        for con in data:
            con = con.split(',')
            ips.append(con[0])
            ports.append(int(con[1]))
            ids.append(int(con[2]))
            keys.append(con[3])
            if (con[0] == host):
                myid = int(con[2])
        c.close()
        writetofile()

    mynode = node.Node(ips, ports, ids, myid, keys)
    
    while True:
        c, addr = s.accept()
        message = None
        message = (c.recv(4096)).decode('ascii')
        if (message == 'Update'):
            response = {'chain': mynode.chain, 'length': len(mynode.chain)}
            response = json.dumps(response)
            t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            t.connect((addr[0], 12345))
            t.send(msg.encode('ascii'))
            t.close()
        else:
            print(message)
            received = json.loads(message, object_pairs_hook=OrderedDict)
            if 'transaction' in received:
                print('Transaction received')
                valid_tran = mynode.validate_transaction(received)
            elif 'block' in received:
                print('Block received')
                valid_block = mynode.validate_block(received)
                if (valid_block == False):
                    request_chain(myid)
            else:
                print('Chain received')
                mynode.resolve_conflicts(received)
        c.close()
    s.close()


if __name__ == '__main__':
    Main()
