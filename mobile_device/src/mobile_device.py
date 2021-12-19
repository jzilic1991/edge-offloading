from utilities import OffloadingSiteCode, OffloadingActions


class MobileDevice:

    def __init__(self, mips, memory, data_storage):
        self._mips = mips
        self._memory = memory
        self._data_storage = data_storage
    
        self._edge_servers = None
        self._cloud_dc = None
        self._mobile_app = None
        self._network = None
        self._ode = None
        self._memory_consumption = 0
        self._data_storage_consumption = 0
        self._name = "MOBILE_DEVICE"
        self._offloading_site_code = OffloadingSiteCode.MOBILE_DEVICE
        self._offloading_action_index = OffloadingActions.MOBILE_DEVICE
        self._discrete_epoch_counter = 0
        self._stats_log = tuple()
        self._sensitivity_analysis = False
        self._energy_supply_budget = 34200 # joules


    def print_system_config(cls):
        print("################### MOBILE DEVICE SYSTEM CONFIGURATION ###################")
        print("CPU: " + str(cls._mips) + " M cycles")
        print("Memory: " + str(cls._memory) + " Gb")
        print("Data Storage: " + str(cls._data_storage) + " Gb")
        print('\n\n')
