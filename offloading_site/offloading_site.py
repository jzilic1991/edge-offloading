from utilities import OffloadingSiteCode, ExecutionErrorCode, OffloadingActions, DatasetType, FailureEventMode, OdeType
from dataset import Dataset

# constants
GIGABYTES = 1000000

class OffloadingSite:

	def __init__(self, mips, memory, data_storage, offloading_site_code, name):
		self.__evaluate_params (mips, memory, data_storage, offloading_site_code)

		self._mips = mips
		self._memory = memory
		self._data_storage = data_storage
		self._offloading_site_code = offloading_site_code
		self._node_candidate = node_candidate

		# prefix name is added according to offloading site type
		if self._offloading_site_code in [OffloadingSiteCode.EDGE_DATABASE_SERVER, OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER, \
			OffloadingSiteCode.EDGE_REGULAR_SERVER]:

			if self._offloading_site_code == OffloadingSiteCode.EDGE_DATABASE_SERVER:
				self._name = 'EDGE_DATABASE_SERVER_' + str(name)
				self._offloading_action_index = OffloadingActions.EDGE_DATABASE_SERVER

			elif self._offloading_site_code == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
				self._name = 'EDGE_COMPUTATIONAL_SERVER_' + str(name)
				self._offloading_action_index = OffloadingActions.EDGE_COMPUTATIONAL_INTENSIVE_SERVER

			elif self._offloading_site_code == OffloadingSiteCode.EDGE_REGULAR_SERVER:
				self._name = 'EDGE_REGULAR_SERVER_' + str(name)
				self._offloading_action_index = OffloadingActions.EDGE_REGULAR_SERVER

		elif self._offloading_site_code == OffloadingSiteCode.CLOUD_DATA_CENTER:
			self._name = "CLOUD_DATA_CENTER_" + str(name)
			self._offloading_action_index = OffloadingActions.CLOUD_DATA_CENTER

		self._memory_consumption = 0
		self._data_storage_consumption = 0
		self._failure_provider = None
		self._dataset_stats = None
		self._svr = None
		self._discrete_epoch_counter = 0
		self._failure_event_mode = None
		self._failure_cnt = 0


	def print_system_config(cls):
		print ("################### " + cls._name  +" SYSTEM CONFIGURATION ###################")
		print ("Name: " + cls._name)
		print ("CPU: " + str(cls._mips) + " M cycles")
		print ("Memory: " + str(cls._memory) + " Gb")
		print ("Data Storage: " + str(cls._data_storage) + " Gb")


        def __evaluate_params(cls, cpu, memory, data_storage, offloading_site_code):
		if cpu <= 0 or type(cpu) is not int:
			raise ValueError("CPU should be positive integer!")

		if memory <= 0 or type(memory) is not int:
			raise ValueError("Memory should be positive integer!")

		if data_storage <= 0 or type(data_storage) is not int:
			raise ValueError("Input data should be positive integer!")

		if isinstance(offloading_site_code, OffloadingSiteCode):
			raise TypeError("Offloadable site code should be OffloadingSiteCode class object!")
