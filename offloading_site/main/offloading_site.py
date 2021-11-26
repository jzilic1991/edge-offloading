from utilities import Util, OffloadingSiteCode, OffloadingActions

# constants
GIGABYTES = 1000000

class OffloadingSite:

    def __init__(self, mips, memory, data_storage, offloading_site_code, name):
        self.__evaluate_params (mips, memory, data_storage, offloading_site_code)

        self._mips = mips
        self._memory = memory
        self._data_storage = data_storage
        self._offloading_site_code = offloading_site_code
        self._socket_client = None
            
        (self._name, self._offloading_action) = Util.determine_name_and_action (name, offloading_site_code)


    def print_system_config(cls):
        print ("################### " + cls._name  +" SYSTEM CONFIGURATION ###################")
        print ("Name: " + cls._name)
        print ("CPU: " + str(cls._mips) + " M cycles")
        print ("Memory: " + str(cls._memory) + " Gb")
        print ("Data Storage: " + str(cls._data_storage) + " Gb")
        print ("Offloading Action: " + str(cls._offloading_action))


    def __evaluate_params(cls, cpu, memory, data_storage, offloading_site_code):
        if cpu <= 0 or type(cpu) is not int:
            raise ValueError("CPU should be positive integer!")

        if memory <= 0 or type(memory) is not int:
            raise ValueError("Memory should be positive integer!")

        if data_storage <= 0 or type(data_storage) is not int:
            raise ValueError("Input data should be positive integer!")

        if isinstance(offloading_site_code, OffloadingSiteCode):
            raise TypeError("Offloadable site code should be OffloadingSiteCode class object!")
