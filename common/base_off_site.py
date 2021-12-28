import sys
from abc import ABC, abstractmethod

from utilities import Util, OffloadingSiteCode, OffloadingActions, NodeType, ExecutionErrorCode
from task import Task

# constants
GIGABYTES = 1000000


class BaseOffloadingSite (ABC):

    def __init__(self, mips, memory, data_storage, node_type, name):
        self.__evaluate_params (mips, memory, data_storage, node_type)

        self._mips = mips
        self._memory = memory
        self._data_storage = data_storage
        self._socket_client = None
        self._data_storage_consumption = 0
        self._memory_consumption = 0
            
        self._off_site_code = Util.determine_off_site_code (node_type)
        (self._name, self._off_action) = Util.determine_name_and_action (name, self._off_site_code)
        self.print_system_config()


    def print_system_config(cls):
        print ("################### " + cls._name  +" SYSTEM CONFIGURATION ###################", file = sys.stdout)
        print ("Name: " + cls._name, file = sys.stdout)
        print ("CPU: " + str(cls._mips) + " M cycles", file = sys.stdout)
        print ("Memory: " + str(cls._memory) + " Gb", file = sys.stdout)
        print ("Data Storage: " + str(cls._data_storage) + " Gb", file = sys.stdout)
        print ("Offloading Action: " + str(cls._off_action), file = sys.stdout)
        print ("Offloading Site Code: " + str(cls._off_site_code), file = sys.stdout)


    def check_validity_of_deployment(cls, task):
        if not isinstance(task, Task):
            return ExecutionErrorCode.EXE_NOK

        # check that task resouce requirements fits offloading sites's resource capacity
        if cls._data_storage > (cls._data_storage_consumption + ((task.get_data_in() + task.get_data_out()) / GIGABYTES)) and \
            cls._memory > (cls._memory_consumption + task.get_memory()):
            return ExecutionErrorCode.EXE_OK


    def __evaluate_params(cls, cpu, memory, data_storage, node_type):
        if cpu <= 0 or type(cpu) is not int:
            raise ValueError("CPU should be positive integer! Value: " + str(cpu))

        if memory <= 0 or type(memory) is not int:
            raise ValueError("Memory should be positive integer! Value: " + str(memory))

        if data_storage <= 0 or type(data_storage) is not int:
            raise ValueError("Input data should be positive integer! Value: " + str(data_storage))

        if isinstance (node_type, NodeType):
            raise TypeError("Offloadable site code should be OffloadingSiteCode class object! Value: " + str(type(node_type)))


    @abstractmethod
    def get_fail_trans_prob (cls):
        pass

    
    @abstractmethod
    def get_server_fail_prob (cls):
        pass


    @abstractmethod
    def get_net_fail_prob (cls):
        pass


    @abstractmethod
    def reset_test_data (cls):
        pass


    @abstractmethod
    def execute (cls, task):
        pass


    @abstractmethod
    def terminate_task (cls, task):
        pass


    @abstractmethod
    def detect_failure_event (cls, prob):
        pass
