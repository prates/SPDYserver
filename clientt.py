'''
Created on Jul 26, 2011

@author: prates
'''

import socket
import streamStruct

class client(object):
    sock = None
    streamID=1
    def __init__(self, server, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server, port))
    
    def run(self): 
        self.send()
        print 'teste'
        
    def send(self):
        pack = streamStruct.Pack(1)
        name = streamStruct.NameValue()
        name.addValue('host', 'localhost')
        data = name.make()
        data = pack.synStream(0, self.streamID, 0, 3, data)
        self.sock.send(data)
    
    def receive(self):
        pass
        
    
        
b=client('',8001)
b.send()
