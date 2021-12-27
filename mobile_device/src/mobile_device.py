import datetime

from utilities import OffloadingSiteCode, OffloadingActions, ExecutionErrorCode, MobApps
from resource_monitor import ResourceMonitor


class MobileDevice:

    def __init__(self, mips, memory, data_storage):
        self._mips = mips
        self._memory = memory
        self._data_storage = data_storage
    
        self._mobile_app = None
        self._network = None
        self._ode = None
        self._res_monitor = ResourceMonitor ()
        #self._edge_servers = self._res_monitor.get_edge_servers ()
        #self._cloud_dc = self._res_monitor.get_cloud_dc ()
        self._memory_consumption = 0
        self._data_storage_consumption = 0
        self._name = "MOBILE_DEVICE"
        self._offloading_site_code = OffloadingSiteCode.MOBILE_DEVICE
        self._offloading_action_index = OffloadingActions.MOBILE_DEVICE
        self._discrete_epoch_counter = 0
        self._stats_log = tuple()
        self._energy_supply_budget = 34200
        self._applications = {MobApps.ANTIVIRUS: 0.05, MobApps.GPS_NAVIGATOR: 0.3, MobApps.FACERECOGNIZER: 0.1, \
                MobApps.FACEBOOK: 0.45, MobApps.CHESS: 0.1}


    def print_system_config(cls):
        print("################### MOBILE DEVICE SYSTEM CONFIGURATION ###################")
        print("CPU: " + str(cls._mips) + " M cycles")
        print("Memory: " + str(cls._memory) + " Gb")
        print("Data Storage: " + str(cls._data_storage) + " Gb")
        print('\n\n')


    def run(cls, samplings, executions):
        #if not cls._ode:
        #    return ExecutionErrorCode.EXE_NOK
        
        previous_progress = 0
        current_progress = 0

        #print("**************** PROGRESS with " + cls._ode.get_name() + "****************")
        print(str(previous_progress) + "% - " + str(datetime.datetime.utcnow()))

        for i in range(samplings):
            application_time_completion = 0
            application_energy_consumption = 0
            application_overall_rewards = 0 
            application_fail_time_completion = 0
            application_fail_energy_consumption = 0
            application_failures = 0
            curr_bandwidth_consumption = 0
            offloading_attempts = 0

            # reset test data after each simulation sampling to start from the beginning
            cls._res_monitor.reset_test_data ()

            # simulate application executions   
            for j in range(executions):
                choice = np.random.choice(MobApps.length, 1, p =[prob for _, prob in cls._applications.items()])[0]

                if choice == 0:
                    cls.deploy_antivirus_application()

                elif choice == 1:
                    cls.deploy_gps_navigator_application()

                elif choice == 2:
                    cls.deploy_facerecognizer_application()

                elif choice == 3:
                    cls.deploy_facebook_application()

                elif choice == 4:
                    cls.deploy_chess_application()

                # cls._ode.save_app_name(cls._mobile_app.get_name())

                previous_progress = current_progress
                current_progress = round((j + (i * executions)) / (samplings * executions) * 100)

                if current_progress != previous_progress and (current_progress % PROGRESS_REPORT_INTERVAL == 0):
                    print(str(current_progress) + "% - " + str(datetime.datetime.utcnow()))

                cls._mobile_app.run()

                ready_tasks = cls._mobile_app.get_ready_tasks()

                single_app_exe_task_comp = 0
                single_app_exe_energy_consum = 0
