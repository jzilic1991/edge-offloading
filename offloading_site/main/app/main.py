from flask import Flask, request, jsonify

from socket_client import SocketClient

#off_site = OffloadingSite(5000, 8, 300, OffloadingSiteCode.EDGE_DATABASE_SERVER, 'A')

app = Flask(__name__)
socket = SocketClient("localhost", 8000)


@app.route('/get_avail_data')
def get_avail_data():
    sysid = request.args.get('sysid', None)
    nodenum = request.args.get('nodenum', None)

    if sysid == None or nodenum == None:
        return jsonify([])

    socket.connect()
    socket.send(str(sysid) + "_" + str(nodenum))
    avail_data = socket.receive()
    socket.close()

    return avail_data


if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000, debug = True)
