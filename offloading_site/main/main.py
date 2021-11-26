import sys
import socket
import pickle
import select
from flask import Flask, request, jsonify

from offloading_site import OffloadingSite
from utilities import OffloadingSiteCode


off_site = OffloadingSite(5000, 8, 300, OffloadingSiteCode.EDGE_DATABASE_SERVER, 'A')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8000))

app = Flask(__name__)


@app.route('/get_avail_data')
def get_avail_data():
    system_id = request.args.get('sysid', None)
    node_num = request.args.get('nodenum', None)
    avail_data = b""
    
    client_socket.send((str(system_id) + '_' + str(node_num)).encode())
    client_socket.setblocking(False)

    while True:
        if select.select([client_socket], [], [], 10)[0]:
            packet = client_socket.recv(4096)
        
        if not packet:
            break
        
        avail_data += packet

    return jsonify (pickle.loads(avail_data))


if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000, debug = True)
