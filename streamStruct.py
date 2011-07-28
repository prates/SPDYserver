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

''''
corrigido bugs, relativos ao empacotamento dos dados
26/07/2011
Alexandre Prates
'''


import xdrlib
from zlib import *


class Pack(object):
    __version=1
    def __init__(self, version):
        if(type(version)==int):
            self.__version = version
        else:
            raise ValueError("Version is an interge.")

    def synStream(self, flag, stream_id, associate, priority, data):
        if(type(flag)==int and type(stream_id)==int and type(associate)==int and type(priority)==int):
            st = xdrlib.Packer()
            st.pack_uint(priority<<28)
            byte = st.get_buffer()
            st.reset()
            byte=byte[:2]
            st.pack_uint(0x40000000 + (self.__version<<16) + 1)
            st.pack_uint((flag<<24) + len(data)+10)
            st.pack_uint(stream_id)
            st.pack_uint(associate)
            return st.get_buffer()+byte+data
        else:
            raise ValueError('value error.')
        
    def synReplay(self, flag, stream_id, data):
        if(type(flag)==int and type(stream_id)==int and type(data)==str):
            st = xdrlib.Packer()
            st.pack_uint(0x40000000 + (self.__version<<16) + 2)
            st.pack_uint((flag<<24) + len(data)+4)
            st.pack_uint(stream_id)
            return st.get_buffer()+data
        else:
            raise ValueError('value error')
    
    def header(self, flag, stream_id, data):
        if(type(flag)==int and type(stream_id)==int and type(data)==str):
            st = xdrlib.Packer()
            st.pack_uint(0x40000000 + (self.__version<<16) + 8)
            print len(data)
            st.pack_uint((flag<<24) + len(data)+8)
            st.pack_uint(stream_id)
            return st.get_buffer() + data
        else:
            raise ValueError('value error')
        
    def FrameData(self, streamID, flag, data):
        if(type(streamID)==int and type(flag)==int and type(data)==str):
            st=xdrlib.Packer()
            st.pack_uint(streamID)
            st.pack_uint((flag<<24) + len(data))
            st.pack_string(compress(data,9))
            return st.get_buffer()
        else:
            raise ValueError('error in value.')
    
    def ping(self, ID):
        if(type(ID)==int):
            st = xdrlib.Packer()
            st.pack_uint(0x40000000 + (self.__version<<16) + 6)
            st.pack_uint(4)
            st.pack_uint(ID)
            return st.get_buffer()
        else:
            raise ValueError("VAlue ID is an interge.")
        
    
    def goaway(self, last_good_stream, status_code):
        if(type(last_good_stream)==int and type(status_code)==int):
            st=xdrlib.Packer()
            st.pack_uint(0x40000000 + (self.__version<<16) + 7)
            st.pack_uint(8)
            st.pack_uint(last_good_stream)
            st.pack_uint(status_code)
            return st.get_buffer()
        else:
            raise ValueError('value of last_good_id is interge and status_code is bool')
  
    def setting(self, flag, data):
        if(type(flag)==int and type(data)==int):
            st = xdrlib.Packer()
            st.pack_uint(0x40000000 + (self.__version<<16) + 4)
            st.pack_uint((flag<<24) + len(data))
            return st.get_buffer()+data
        else:
            raise ValueError('value error')
        
        
    def resetStream(self, stream_id, status_code):
        if(type(stream_id)==int and type(status_code)==int):
            st = xdrlib.Packer()
            st.pack_uint(0x40000000 + (self.__version<<16) + 3)
            st.pack_uint(8)
            st.pack_uint(stream_id)
            st.pack_uint(status_code)
            return st.get_buffer()
        else:
            raise ValueError("The values of stream_id and status_code are interge.")
    
    def windowsUpdate(self, stream_id, windows_size):
        if(type(stream_id)==int and type(windows_size)==int):
            st = xdrlib.Packer()
            st.pack_uint(0x40000000 + (self.__version<<16) + 9)
            st.pack_uint(8)
            st.pack_uint(stream_id)
            st.pack_uint(windows_size)
            return st.get_buffer()
        else:
            raise ValueError('The values of stream_id and windows_size are interge.')
    
    def versions(self, flag, data):
        if(type(flag)==int and type(data)==list):
            st = xdrlib.Packer()
            temp = ''
            for i in data:
                st.pack_uint(i)
                a = st.get_buffer()
                st.reset()
                temp+=a[:2]
            st.pack_uint(0x40000000 + (self.__version<<16) + 10)
            st.pack_uint((flag<<24) + (len(data)*2))
            return st.get_buffer()+data
        else:
            raise ValueError('value error.')
        
class Unpack(object):
    __buffer=''
    
    def __init__(self, buffer):
        self.__buffer = buffer
    
    def extract(self):
        ret = {}
        st=xdrlib.Unpacker(self.__buffer)
        header1 = st.unpack_uint()
        header2 = st.unpack_uint()
        if((header1&0x40000000)>>30==1):
            ret['control'] = (header1&0x40000000)>>30
            ret['version'] = (header1&0x3fff0000)>>16
            ret['type'] = header1&0xffff
            ret['flag'] = (header2&0x7f000000)>>24
            ret['length'] = header2&0x00ffffff
            if(ret['type']==7):
                if(ret['length']==8):#FRAME GOAWAY
                    ret['last_god_stream'] = st.unpack_uint()
                    ret['statuscode'] = st.unpack_uint()
                    
                else:
                    raise ValueError('Error: length of frame goaway is 8 bytes')
                
            elif(ret['type']==6):#FRAME PING
                if(ret['length']==4):
                    ret['ID']=st.unpack_uint()
                else:
                    raise ValueError('Error: length of frame PING is 4 bytes')
                
            elif(ret['type']==3):#FRAME RST_STREAM
                if(ret['length']==8):
                    ret['streamId'] = st.unpack_uint()
                    ret['statusCode'] = st.unpack_uint() 
                    
                else:
                    raise ValueError('Error: length of RST_STREAM is 8 bytes')
            
            elif(ret['type']==1):#syn_stream
                #d=['streamId', 'associate', 'priority', 'numberPair', 'nameValues']
                #data = dict.fromkeys(tuple(d))
                ret['streamId'] = st.unpack_uint()
                ret['associate'] = st.unpack_uint()
                priority = st.unpack_uint()
                priority = (priority&0x70000000)>>26
                ret['priority'] = priority
                temp = st.get_buffer()
                temp = temp[18:]
                #name = st.unpack_string()
                if(ret['length']==(len(temp)+10)):  
                    name = NameValue()
                    ret['nameValue'] = name.extract(temp)
                    ret['numberPair'] = len(ret['nameValue'])
                    #ret['data'] = data
                else:
                    raise ValueError('Error in length of the frame.')
           
            elif(ret['type']==2):#FRAME SYN-REPLY
                ret['streamId'] = st.unpack_uint()
                temp = st.get_buffer()
                temp = temp[12:]
                #name = st.unpack_string()
                if(ret['length']==len(temp)+4):
                    name = NameValue()
                    ret['nameValue'] = name.extract(temp)
                    ret['numberPair'] = len(ret['nameValue'])
                    
                else:
                    raise ValueError('Error in length of the frame.')

            elif(ret['type']==8):#FRAME HEADER
                ret['streamId'] = st.unpack_uint()
                temp = st.get_buffer()
                temp = temp[12:]
                print ret
                print len(temp)
                if(ret['length']==(len(temp)+8)):
                    name = NameValue()
                    ret['nameValue'] = name.extract(temp)
                    ret['numberPair'] = len(ret['nameValue'])
                   
                else:
                    raise ValueError('Error in length of frame.')
                
            elif(ret['type']==9):
                if(ret['length']!=8):
                    raise ValueError('Error in length of frame.')
                ret['streamId'] = st.unpack_uint()
                ret['windows_size'] = st.unpack_uint()

#            elif(ret['type']==10):#FRAME VERSION
#                d=['numberversion', 'data']
#                data = dict.fromkeys(tuple(d))
#                data['numberversion'] = st.unpack_uint()
#                data['data']=version.getlistvesion(self, data)

            else:
                raise error("Value of frame not exist.")
            
        else:
            ret['control'] = 0
            ret['streamID'] = header1
            ret['flag'] = (header2&0x7f000000)>>24
            ret['length'] = header2&0x00ffffff
            ret['data'] = decompress(st.unpack_string())
            
        return ret  
    
    
                
'''                
class version(object):
    #implementar
    __version=''
    def add(self, version):
        if(type(version)==int and version<0xffff):
            st=xdrlib.Packer()
            st.pack_uint(version)
            i = st.get_buffer()
            self.__version += i[2:] 
            
    def getVersions(self):
        return len(self.__version)/2
    
    def getlistvesion(self, data):
        version=[]
        temp=''
        for i in range(len(data)):
            temp+=st.unpack_string[1]
            if( i > 1 and i%2==0):ret['data'] = temp
                st=xdrlib.Unpacker(temp)
                version.append(st.unpack_uint())
                temp=''
        return version
'''
             
class setting(object):
    __sett=[]
    
    def add(self,flag, id, values):
        if(type(id)==int and type(values)==int):
            self.__sett.append((((flag<<24)+id), values))              
        else:
            raise ValueError('Values of id and values are interge.')    
                
    def remove(self, flag, id, values):
        if(type(id)==int and type(values)==int and type(flag)==int):
            id = (flag<<24)+id
            self.__sett.remove((((flag<<24)+id), values))              
        else:
            raise ValueError('Values of id and values are interge.')    
    
    
    def make(self):
        st = xdrlib.Packer()
        st.pack_uint(len(self.__sett))
        for i in self.__sett:
            st.pack_uint(i[0])
            st.pack_uint(i[1])
        return st.get_buffer()
    
    def extract(self, data):
        if(type(data)==str):
            st = xdrlib.Unpacker(data)
            length = st.unpack_uint()
            ret=[]
            for i in range(length):
                temp=[]
                t = st.unpack_uint()
                temp.append(t>>24)
                temp.append(t&0x00ffffff)
                if(temp[0]>255):
                    raise ValueError('value of flag < 255.')
                temp.append(st.unpack_uint())
                ret.append(tuple(temp))
            return ret
        else:
            raise ValueError('value of data is string.')
    
    
    
                
class NameValue(object):
    __nameValue=[]

    def addValue(self, name, value):
        if (type(name) == str and type(value) == str):
            self.__nameValue.append((len(name), name, len(value), value)) 
        else:
            raise ValueError('name and value is a string !!!!')    


    def removeValue(self, name, value):
        if (type(name)  == str and type(value) == str):
            self.NameValue.remove((len(name), name, len(value), value))
        else:
            raise ValueError('name and value is a string!!!!')
      
    def make(self):
        st = xdrlib.Packer()
        st.pack_uint(len(self.__nameValue))
        for i in self.__nameValue:
            st.pack_uint(i[0])
            st.pack_string(i[1])
            st.pack_uint(i[2])
            st.pack_string(i[3])
        
        return compress(st.get_buffer(),9)
            
                
        
    def extract(self, data):
        if(type(data)==str):
            st = xdrlib.Unpacker(decompress(data))
            length = st.unpack_uint()
            ret=[]
            for i in range(length):
                temp=[]
                temp.append(st.unpack_uint())
                temp.append(st.unpack_string())
                temp.append(st.unpack_uint())
                temp.append(st.unpack_string())
                ret.append(tuple(temp))
            if(len(ret)!=length):
                raise ValueError('Error in length of name/value block')    
            print ret
            return ret
                
        else:
            raise ValueError('Data is a string')
        
    def getNamevalue(self):
        return self.__nameValue


if(__name__=='__main__'):
    
    
    #FALTA IMPLEMENTAR O CAMPO ID/VALUE NA FRAME SETTING na compressao
    #falta implementar as frames settings e version na extracao'
    
    #teste area
    
    a=Pack(1)
    name = NameValue()
    name.addValue('teste', 'teste')
    data = a.synStream(1, 1, 0, 2, name.make())
    print data
    e = Unpack(data)
    data = e.extract()
    print data
    data = a.synReplay(1, 1, name.make())
    print data
    e=Unpack(data)
    print e.extract()
    data = a.resetStream(1, 1)
    print data
    e=Unpack(data)
    print e.extract()
    data = a.ping(1)
    print data
    e=Unpack(data)
    print e.extract()
    data = a.goaway(1, 1)
    print data
    e=Unpack(data)
    print e.extract()
    data = a.FrameData(1, 1, 'teste')
    print data
    e=Unpack(data)
    print e.extract()
    data = a.header(1, 1, name.make())
    print "------------------------------"
    print name.make()
    e=Unpack(data)
    print e.extract()
    data = a.windowsUpdate(1, 100)
    print data
    e=Unpack(data)
    print e.extract()
    se = setting()
    se.add(1, 3, 5)
    se.make()
    
    '''
    verificar frame setting e testar
    '''