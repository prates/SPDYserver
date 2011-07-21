'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Created on May 22, 2011

@author: Alexandre Prates
'''


import socket
from streamSpdy import Pack, unpack
from heapq import heappush, heappop
import thread

class Server():
    sock = None
    
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('',port))
        self.sock.setblocking(0)
            
    def tcpConn(self):
        self.sock.listen(1)
        (sockaddr, cli) = self.sock.accept()
        return  (sockaddr, cli)
    
    def send(self,cli, data):
        cli.send(data)
        
    def rec(self, cli):
        data = cli.recv(1024)
        return data
    def close(self):
        thread.exit_thread()
        self.close()
    
class SPDYServer():
    #implementar threadS
    __versions = []
    __SETTINGS_UPLOAD_BANDWIDTH = 0
    __SETTINGS_DOWNLOAD_BANDWIDTH = 0
    __SETTINGS_ROUND_TRIP_TIME = 0
    __SETTINGS_MAX_CONCURRENT_STREAMS = 0
    __SETTINGS_CURRENT_CWND = 0
    __stream = [] #list of priority stream
    __bufferstream={} #stream active
    idstream = 2
    
    def run(self):
        conn = Server(8000)
        conn.tcpConn()
        thread.start_new_thread(receive, conn)
        
        
            
    def receive(self, conn):
        while True:
            data = conn.rec()
            frame = unpack(data)
            if not(frame['streamID'] in self.__bufferstream):#receiver new stream
                if (frame['control']==1):
                    if(frame['type']==1):
                        if(frame['streamID']%2==1):
                            heappush(self.__stream, [frame['priority'], frame['streamID']])
                            self.__bufferstream[frame['streamID']] = 1
                elif (frame['type']==3):
                    del self.__bufferstream[frame['streamID']]
                    for i in self.__stream:
                        if i[1]==frame['streamID']:
                            self.__stream.remove(i)
                elif (frame['type']==8):
                    del self.__bufferstream
                    del self.__stream
                    conn.close()
                   
            elif (frame['control']==0):
                if not(frame['streamID'] in self.__bufferstream):
                #eception
        
       
#exception
        
        


a= Server(8006)
print "porta aberta"
(s, c) = a.tcpConn()
a.send(s, 'teste')
print a.rec(s)
