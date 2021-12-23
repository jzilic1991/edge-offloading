import re

from base_off_site import BaseOffloadingSite
from socket_client import SocketClient
from utilities import OffloadingSiteCode


class RemoteOffloadingSite (BaseOffloadingSite):

    def __init__ (self, mips, memory, storage, node_type, name):
        super().__init__(mips, memory, storage, node_type, name)
        self._sock_fail_mon = SocketClient ("localhost", 8000)
        self._sock_pred_engine = SocketClient ("localhost", 8001)
        self._node_candidates = self.__parse_node_candidate_list()
        
        self.__send_candidate_list ()
         

    def get_fail_trans_prob (cls):
        raise NotImplementedError

    
    def get_server_fail_prob (cls):
        raise NotImplementedError


    def get_net_fail_prob (cls):
        raise NotImplementedError


    def reset_test_data (cls):
        raise NotImplementedError


    def execute (cls, task):
        raise NotImplementedError


    def terminate_task (cls, task):
        raise NotImplementedError


    def detect_failure_event (cls, prob):
        raise NotImplementedError


    def __parse_node_candidate_list (cls):
        node_candidates = list ()
        filepath = cls.__deter_cand_list_file_path ()

        with open (filepath, 'r') as fileobj:
            line = fileobj.readline()

            while line:
                result = re.findall ('\((\d+),(\d+)\)', line)
                node_candidates.append((int(result[0][0]), int(result[0][1])))
                line = fileobj.readline()

        return node_candidates
    
    
    def __send_candidate_list (cls):
        cls._sock_fail_mon.connect()
        cls._sock_fail_mon.send (pickle.dumps(cls._node_candidates))
        fail_data = sock_fail_mon.receive()
        cls._sock_fail_mon.close()


    def __deter_cand_list_file_path (cls):
        if cls._off_site_code == OffloadingSiteCode.EDGE_DATABASE_SERVER:
            return 'node_candidate/edge_database.txt'

        elif cls._off_site_code == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
            return 'node_candidate/edge_computational.txt'

        elif cls._off_site_code == OffloadingSiteCode.EDGE_REGULAR_SERVER:
            return 'node_candidate/edge_regular.txt'

        elif cls._off_site_code == OffloadingSiteCode.CLOUD_DATA_CENTER:
            return 'node_candidate/cloud_dc.txt'
