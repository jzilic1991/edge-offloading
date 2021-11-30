import sys
import select
import pickle
from flask import jsonify


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
    

    def send (cls, str_text):
        cls._socket.send (str_text.encode())


    def receive (cls):
        avail_data = b""
        packet = None

        cls._socket.setblocking (False)

        while True:
            if select.select([cls._socket], [], [], 10)[0]:
                packet = cls._socket.recv(4096)
        
            if not packet:
                break
        
            avail_data += packet
        
        if avail_data == b"":
            return jsonify([])
        
        return jsonify (pickle.loads(avail_data))


    def close (cls):
        print ('Socket connection with ' + str(cls._socket.getpeername()) + ' is closing!', file = sys.stdout)
        cls._socket.close()
