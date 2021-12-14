import sys
import select
import pickle
import datetime


class SocketClient():

    def __init__ (self, host, port):
        self._socket = None
        self._host = host
        self._port = port


    def connect (cls):
        import socket
        
        cls._socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        cls._socket.connect ((cls._host, cls._port))

        print ('Socket connection with ' + str(cls._socket.getpeername()) + ' is established!', file = sys.stdout)
    

    def send (cls, data):
        if isinstance (data, str):
            cls._socket.send (data.encode())
        
        elif isinstance (data, bytes):
            cls._socket.send (data)


    def receive (cls):
        data = b""
        packet = None

        while True:
            if select.select([cls._socket], [], [])[0]:
                packet = cls._socket.recv(4096)
        
            if not packet:
                break
        
            data += packet
        
        if data == b"":
            return []
        
        return pickle.loads(data)


    def close (cls):
        print ('Socket connection with ' + str(cls._socket.getpeername()) + ' is closing!', file = sys.stdout)
        cls._socket.close()
