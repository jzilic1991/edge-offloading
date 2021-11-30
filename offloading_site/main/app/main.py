import pickle
from flask import Flask, request, jsonify

from socket_client import SocketClient

#off_site = OffloadingSite(5000, 8, 300, OffloadingSiteCode.EDGE_DATABASE_SERVER, 'A')

app = Flask(__name__)
sock_fail_mon = SocketClient ("localhost", 8000)
sock_pred_engine = SocketClient ("localhost", 8001)


@app.route('/get_avail_data')
def get_avail_data():
    sysid = request.args.get('sysid', None)
    nodenum = request.args.get('nodenum', None)

    if sysid == None or nodenum == None:
        return jsonify([])

    sock_fail_mon.connect()
    sock_fail_mon.send(str(sysid) + "_" + str(nodenum))
    fail_data = socket_fail_mon.receive()
    socket_fail_mon.close()

    sock_pred_engine.connect()
    sock_pred_engine.send(pickle.dumps(fail_data))
    avail_data = pickle.loads(sock_pred_engine.receive())
    socket_fail_mon.close()

    return avail_data


if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000, debug = True)
