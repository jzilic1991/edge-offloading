import sys
import re
from pathlib import Path
from kivy.network.urlrequest import UrlRequest

from base_off_site import BaseOffloadingSite
from utilities import OffloadingSiteCode


class RepresentOffloadingSite (BaseOffloadingSite):

    def __init__ (self, mips, memory, storage, node_type, url_svc, name):
        super().__init__(mips, memory, storage, node_type, name)
        self._url_svc = url_svc
        self._node_candidates = self.__parse_node_candidate_list ()
        self._iter_index = -1
        self._avail_data = list ()
        self._used_data = list ()


    def get_url_svc (cls):
        return cls._url_svc


    def next_node_candidate (cls):
        cls._iter_index += 1
        cls._iter_index %= len(cls._node_candidates)

        filepath = 'cached_avail_data/' + str(cls._node_candidates[cls._iter_index][0]) + '_' +\
            str(cls._node_candidates[cls._iter_index][1]) + '.txt'
    
        if Path(filepath).exists():
            cls._avail_data = cls.__read_avail_dist (filepath)
        
        else:
            cls._avail_data = cls.__create_avail_dist_file (filepath, cls._node_candidates[cls._iter_index])

        cls._used_data = cls._avail_data
        

    def get_fail_trans_prob (cls):
        if len(cls._used_data) == 0:
            cls._used_data = cls._avail_data
        
        fail_prob = cls._used_data[0]
        del cls._used_data[0]
        return fail_prob

    
    def get_server_fail_prob (cls):
        return 0.9


    def get_net_fail_prob (cls):
        return 0.1


    def reset_test_data (cls):
        if len(cls._avail_data) != 0:
            cls._used_data = cls._avail_data
            return
        
        filepath = 'cached_avail_data/' + str(cls._node_candidates[cls._iter_index][0]) + '_' +\
            str(cls._node_candidates[cls._iter_index][1]) + '.txt'
        
        if not Path(filepath).exists():
            cls._avail_data = cls.__create_avail_dist_file (filepath, cls._node_candidates[cls._iter_index])
        
        cls._avail_data = cls.__read_avail_dist (filepath)
        cls._used_data = cls._avail_data        


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
    

    def __deter_cand_list_file_path (cls):
        if cls._off_site_code == OffloadingSiteCode.EDGE_DATABASE_SERVER:
            return 'node_candidate/edge_database.txt'

        elif cls._off_site_code == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
            return 'node_candidate/edge_computational.txt'

        elif cls._off_site_code == OffloadingSiteCode.EDGE_REGULAR_SERVER:
            return 'node_candidate/edge_regular.txt'

        elif cls._off_site_code == OffloadingSiteCode.CLOUD_DATA_CENTER:
            return 'node_candidate/cloud_dc.txt'
    

    def __read_avail_dist (cls, filepath):
        avail_data = list ()
        
        print ('Reading availability data from file ' + filepath, file = sys.stdout)

        with open (filepath, 'r') as filereader:
           line = filereader.readline()

           while line:
               if re.search ('\d+.\d+', line):
                   avail_data.append(float (line))                
               
               line = filereader.readline()
           
           filereader.close()
        
        return avail_data


    def __create_avail_dist_file (cls, filepath, node_candidate):
        url_path = cls._url_svc + "/get_avail_data?sysid=" + str(node_candidate[0]) + "&nodenum=" + str(node_candidate[1])
        url_req = UrlRequest (url_path, timeout = 30)
        url_req.wait()

        avail_data = url_req.result

        print ('Creating availability file ' + filepath)
        
        with open (filepath, 'w') as filewriter:
            
            for data_point in avail_data:
                filewriter.write (str(data_point) + '\n')

            filewriter.close()
