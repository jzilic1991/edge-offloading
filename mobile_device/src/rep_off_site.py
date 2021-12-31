import sys
import re
import json
from pathlib import Path
from kivy.network.urlrequest import UrlRequest

from base_off_site import BaseOffloadingSite
from utilities import OffloadingSiteCode, ExecutionErrorCode
from task import Task

# constants
GIGABYTES = 1000000

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
            str(cls._node_candidates[cls._iter_index][1]) + '.json'
    
        if Path(filepath).exists():
            cls._avail_data = cls.__read_avail_dist (filepath)
        
        else:
            cls._avail_data = cls.__create_avail_dist_file (filepath, cls._node_candidates[cls._iter_index])

        cls._used_data = cls._avail_data
        

    def get_fail_trans_prob (cls):
        if len(cls._used_data) == 0:
            cls._used_data = cls._avail_data
        
        fail_prob = cls._used_data['predicted'][0]

        if fail_prob > 1:
            fail_prob = 1
        
        if fail_prob >= 0.95 and cls._off_site_code != OffloadingSiteCode.CLOUD_DATA_CENTER:
            return 0

        return (1 - fail_prob)

    
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
        if not isinstance(task, Task):
            raise ValueError("Task for execution on offloading site should be Task class instance!")

        offloadable = task.is_offloadable()

        if not offloadable:
            return ExecutionErrorCode.EXE_NOK

        #if cls._failure_event_mode == FailureEventMode.POISSON_FAILURE:
        #    if cls._failure_event <= cls._discrete_epoch_counter:
        #        return ExecutionErrorCode.EXE_NOK

        #elif cls._failure_event_mode == FailureEventMode.TEST_DATASET_FAILURE:
        #    if cls._failure_event_flag:
        #        return ExecutionErrorCode.EXE_NOK
    
        if not task.execute():
            raise ValueError("Task execution operation is not executed properly! Please check the code of execute() method in Task class!")

        print_text = "Task " + task.get_name()
        task_data_storage_consumption = task.get_data_in() + task.get_data_out()
        task_memory_consumption = task.get_memory()

        cls._data_storage_consumption = cls._data_storage_consumption + (task_data_storage_consumption / GIGABYTES)
        cls._memory_consumption = cls._memory_consumption + task_memory_consumption

        return ExecutionErrorCode.EXE_OK


    def terminate_task (cls, task):
        raise NotImplementedError


    def detect_failure_event (cls, prob):
        raise NotImplementedError
    

    def flush_executed_task(cls, task):
        if not isinstance(task, Task):
            return ExecutionErrorCode.EXE_NOK
    
        cls._memory_consumption = cls._memory_consumption - task.get_memory()
        cls._data_storage_consumption = cls._data_storage_consumption - ((task.get_data_in() + task.get_data_out()) / GIGABYTES)

        if cls._memory_consumption < 0 or cls._data_storage_consumption < 0:
            raise ValueError("Memory consumption: " + str(cls._memory_consumption) + \
                    "Gb, data storage consumption: " + str(cls._data_storage_consumption) + \
                    "Gb, both should be positive! Node: " + cls._name + ", task: " + task.get_name())


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

        with open (filepath, 'r') as jsonfile:
           avail_data  = json.load(jsonfile)
        
        return avail_data


    def __create_avail_dist_file (cls, filepath, node_candidate):
        url_path = cls._url_svc + "/get_avail_data?sysid=" + str(node_candidate[0]) + "&nodenum=" + str(node_candidate[1])
        url_req = UrlRequest (url_path, timeout = 30)
        url_req.wait()

        avail_data = url_req.result

        print ('Creating availability file ' + filepath)
        
        with open (filepath, 'w') as jsonfile:
            json.dump(avail_data, jsonfile)
