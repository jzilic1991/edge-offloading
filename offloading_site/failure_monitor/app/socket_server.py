import sys
import socket
import threading
import pickle

from failure_monitor import FailureMonitor


class SocketServer():

    def __init__ (self, host, port, node_type):
        self._fail_monitor = FailureMonitor ('../data/LANL.csv', node_type)
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
        while True:
            args = conn.recv(4096).decode()
            args = args.split('_')
            sysid, nodenum = args[0], args[1]
            data = cls._fail_monitor.get_avail_data(sysid, nodenum)
            break

        cls.__send (conn, data)


    def __send (cls, conn, data):
        conn.send (pickle.dumps(data))
        conn.close ()


    def __bind (cls):
        cls._socket.bind((cls._host, cls._port))
        cls._socket.listen()

        print ('Socket server is started!', file = sys.stdout)
