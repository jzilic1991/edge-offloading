import sys
import socket
import threading
import pickle
import select
import datetime
import re

from prediction_engine import PredictionEngine


class SocketServer():

    def __init__ (self, host, port):
        self._pred_engine = PredictionEngine ()
        self._socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self._host = host
        self._port = port

        self.__bind()
        
    
    def run (cls):
        while True:
            conn, addr = cls._socket.accept()
            
            print ('Socket connection is started with ' + str(addr), file = sys.stdout)

            client_handler = threading.Thread(target = cls.__receive, args = (conn,))
            client_handler.start()


    def __receive (cls, conn):
        req_data = b""

        while True:
            packet = None
            
            if select.select([conn], [], [], 5)[0]:
                packet = conn.recv(4096)
            
            if not packet:
                break
        
            req_data += packet
        
        load_data = pickle.loads(req_data)
        if req_data == b"" or len(load_data) == 0:
            cls.__send (conn, [])
            return

        if type (load_data) == str:
            if re.search ('\d+_\d+', load_data):
                result = cls._pred_engine.check_cached_files (load_data)
                cls.__send (conn, result)
                return

        print ('Loaded failure data (node: ' + str(load_data[0]) + ') with length ' + str(len(load_data[1])), file = sys.stdout)
        cls.__send (conn, cls._pred_engine.train_and_estimate (load_data[0], load_data[1]))


    def __send (cls, conn, data):
        conn.send (pickle.dumps(data))
        conn.close ()


    def __bind (cls):
        cls._socket.bind((cls._host, cls._port))
        cls._socket.listen()

        print ('Socket server is started!', file = sys.stdout)
