import socket
import sys
import threading
import pickle

from failure_monitor import FailureMonitor


fail_monitor = FailureMonitor('../data/LANL.csv')
server_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8000))
server_socket.listen()

def sock_client_handler (conn):
    while True:
        args = conn.recv(4096).decode()
        args = args.split('_')
        sysid, nodenum = args[0], args[1]
        data = fail_monitor.get_avail_data(sysid, nodenum)
        break
    
    conn.send(pickle.dumps(data))
    conn.close()


if __name__ == "__main__":
    while True:
        conn, addr = server_socket.accept()
        client_handler = threading.Thread(target = sock_client_handler, args = (conn,))
        client_handler.start()
