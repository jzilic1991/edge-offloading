import re
import sys
import pickle

from base_off_site import BaseOffloadingSite
from socket_client import SocketClient
from utilities import OffloadingSiteCode


class RemoteOffloadingSite (BaseOffloadingSite):

    def __init__ (self, mips, memory, storage, node_type, name):
        super().__init__(mips, memory, storage, node_type, name)
        self._sock_fail_mon = SocketClient ("localhost", 8000)
        self._sock_pred_engine = SocketClient ("localhost", 8001)
        self._node_candidates = self.__parse_node_candidate_list()
        
        self.__gen_avail_dist_in_files ()
        

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

    
    def __gen_avail_dist_in_files (cls):
        for node in cls._node_candidates:
            node_candidate = str(node[0]) + '_' + str(node[1])

            print ('Sending node candidate ' + node_candidate + ' to failure monitor!', file = sys.stdout)
            cls._sock_fail_mon.connect()
            cls._sock_fail_mon.send(node_candidate)
            fail_data = cls._sock_fail_mon.receive()
            cls._sock_fail_mon.close()
            print ('Receive failure data with length ' + str(len(fail_data)), file = sys.stdout)
            
            if len(fail_data) == 0:
                continue
            
            print ('Sending node candidate ' + node_candidate + ' to prediction engine!', file = sys.stdout)
            cls._sock_pred_engine.connect()
            cls._sock_pred_engine.send(pickle.dumps(node_candidate))
            avail_data = cls._sock_pred_engine.receive()
            cls._sock_pred_engine.close()
            print ('Receive availability data with lengths ' + str(len(avail_data['actual'])) + \
                    ' and ' + str(len(avail_data['predicted'])) , file = sys.stdout)

            if len(avail_data['actual']) == 0 or len(avail_data['predicted']) == 0:
                print ('Sendind failure data to prediction engine!', file = sys.stdout)
                cls._sock_pred_engine.connect()
                cls._sock_pred_engine.send(pickle.dumps([node_candidate, fail_data]))
                avail_data = cls._sock_pred_engine.receive()
                cls._sock_pred_engine.close()
                print ('Receive availability data with length ' + str(len(avail_data)), file = sys.stdout)
