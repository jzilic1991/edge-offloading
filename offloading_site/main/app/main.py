import sys
import psycopg2
import pickle
import pandas as pd
from flask import Flask, request, jsonify

from socket_client import SocketClient

#off_site = OffloadingSite(5000, 8, 300, OffloadingSiteCode.EDGE_DATABASE_SERVER, 'A')

app = Flask(__name__)
sock_fail_mon = SocketClient ("localhost", 8000)
sock_pred_engine = SocketClient ("localhost", 8001)

def init_off_site ():
    con = psycopg2.connect(database = "postgres", user = "postgres", password = "", host = "10.8.0.1", port = "30226")
    print("Database opened successfully", file = sys.stdout)
    
    cur = con.cursor()
    query = "SELECT * FROM application_tasks";
    cur.execute(query)
    data = cur.fetchall()

    col_names = []
    for elt in cur.description:
        col_names.append(elt[0])

    df = pd.DataFrame(data, columns=col_names)
    print (df, file = sys.stdout)
    con.close()


@app.route('/get_avail_data')
def get_avail_data():
    sysid = request.args.get('sysid', None)
    nodenum = request.args.get('nodenum', None)

    if sysid == None or nodenum == None:
        return jsonify([])

    sock_fail_mon.connect()
    sock_fail_mon.send(str(sysid) + "_" + str(nodenum))
    fail_data = sock_fail_mon.receive()
    sock_fail_mon.close()

    sock_pred_engine.connect()
    sock_pred_engine.send(pickle.dumps(fail_data))
    avail_data = sock_pred_engine.receive()
    sock_pred_engine.close()

    return jsonify (avail_data)


if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000, debug = True)

    init_off_site()
