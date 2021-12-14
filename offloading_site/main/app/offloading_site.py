from utilities import Util, OffloadingSiteCode, OffloadingActions

# constants
GIGABYTES = 1000000

class OffloadingSite:

    def __init__(self, mips, memory, data_storage, node_type, name):
        self.__evaluate_params (mips, memory, data_storage, node_type, name)

        self._mips = mips
        self._memory = memory
        self._data_storage = data_storage
        self._socket_client = None
            
        (self._name, self._offloading_action) = Util.determine_name_and_action (name, offloading_site_code)
        self.offloading_site_code = Util.determine_off_site_code (node_type)


    def print_system_config(cls):
        print ("################### " + cls._name  +" SYSTEM CONFIGURATION ###################")
        print ("Name: " + cls._name)
        print ("CPU: " + str(cls._mips) + " M cycles")
        print ("Memory: " + str(cls._memory) + " Gb")
        print ("Data Storage: " + str(cls._data_storage) + " Gb")
        print ("Offloading Action: " + str(cls._offloading_action))


    def __evaluate_params(cls, cpu, memory, data_storage, node_type, name):
        if cpu <= 0 or type(cpu) is not int:
            raise ValueError("CPU should be positive integer! Value: " + str(cpu))

        if memory <= 0 or type(memory) is not int:
            raise ValueError("Memory should be positive integer! Value: " + str(memory))

        if data_storage <= 0 or type(data_storage) is not int:
            raise ValueError("Input data should be positive integer! Value: " + str(data_storage))

        if isinstance (node_type, NodeType):
            raise TypeError("Offloadable site code should be OffloadingSiteCode class object! Value: " + str(type(node_type)))
