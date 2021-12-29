import datetime

from utilities import OffloadingSiteCode, OffloadingActions, ExecutionErrorCode
from resource_monitor import ResourceMonitor
from mob_app_profiler import MobileAppProfiler
from mdp_svr_ode import MdpSvrOde


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
        self._mobile_app_profiler = MobileAppProfiler ()
        self._mobile_app = None


    def print_system_config(cls):
        print ("################### MOBILE DEVICE SYSTEM CONFIGURATION ###################")
        print ("CPU: " + str(cls._mips) + " M cycles")
        print ("Memory: " + str(cls._memory) + " Gb")
        print ("Data Storage: " + str(cls._data_storage) + " Gb")
        print ('\n\n')


    def deploy_mdp_svr_ode (cls):
        cls._ode = MdpSvrOde(cls, cls._edge_servers, cls._cloud_dc, cls._network, MDP_SVR_ODE_NAME)


    def run(cls, samplings, executions):
        if not cls._ode:
            return ExecutionErrorCode.EXE_NOK
        
        previous_progress = 0
        current_progress = 0

        print ("**************** PROGRESS with " + cls._ode.get_name() + "****************")
        print (str(previous_progress) + "% - " + str(datetime.datetime.utcnow()))

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
                cls._mobile_app = cls._mobile_app_profiler.deploy_random_mobile_app()

                # cls._ode.save_app_name(cls._mobile_app.get_name())

                previous_progress = current_progress
                current_progress = round((j + (i * executions)) / (samplings * executions) * 100)

                if current_progress != previous_progress and (current_progress % PROGRESS_REPORT_INTERVAL == 0):
                    print(str(current_progress) + "% - " + str(datetime.datetime.utcnow()))

                cls._mobile_app.run()
                ready_tasks = cls._mobile_app.get_ready_tasks()
                single_app_exe_task_comp = 0
                
                while ready_tasks:
                        (task_completion_time, task_energy_consumption, task_overall_reward, task_failure_time_cost,\
                                task_failure_energy_cost, task_failures) = cls._ode.offload(ready_tasks)
                        offloading_attempts += task_failures + len(ready_tasks)
                        print ("Failed offloading attemps: " + str(task_failures))
                        print ("Successful offloading attempts:" + str(len(ready_tasks)))
                        print ("Current offloading attempts: " + str(offloading_attempts))
                        ready_tasks = cls._mobile_app.get_ready_tasks()

                        application_time_completion = round(application_time_completion + task_completion_time, 3)
                        application_fail_time_completion += round(task_failure_time_cost, 3)
                        single_app_exe_task_comp = round(single_app_exe_task_comp + task_completion_time, 3)
                        print ("Current application runtime: " + str(application_time_completion) + " s")

                        application_energy_consumption = round(application_energy_consumption + task_energy_consumption, 3)
                        application_fail_energy_consumption = round(application_fail_energy_consumption + task_failure_energy_cost, 3)
                        single_app_exe_energy_consum = round(single_app_exe_energy_consum + task_energy_consumption, 3)
                        print ("Current application energy consumption: " + str(application_energy_consumption) + " J")

                        application_failures += task_failures
                        print ("Current application failures: " + str(application_failures) + '\n')

                        application_overall_rewards = round(application_overall_rewards + task_overall_reward, 3)
                        curr_bandwidth_consumption += epoch_bandwidth_consumption

                        print ("Current application overall rewards: " + str(application_overall_rewards))
                        print ("Current bandwidth consumption: " + str(curr_bandwidth_consumption) + ' kbps\n')
                        print ('Task application runtime: ' + str(task_completion_time) + 's')
                        print ('Task energy consumption: ' + str(task_energy_consumption) + 'J')
                        print ('Task rewards: ' + str(task_overall_reward))
                        print ('Task failure time cost:' + str(task_failure_time_cost) + 's')

                        cls._mobile_app.print_task_exe_status()

                    cls.__reset_application()
                    cls._ode.get_statistics().add_time_comp_single_app_exe(single_app_exe_task_comp)
                    cls._ode.get_statistics().add_energy_consum_single_app_exe(single_app_exe_energy_consum)
                
                cls._ode.get_statistics().add_time_comp(application_time_completion)
                    
                battery_lifetime = (cls._energy_supply_budget - application_energy_consumption) / cls._energy_supply_budget * 100
                cls._ode.get_statistics().add_energy_eff(battery_lifetime)
                cls._ode.get_statistics().add_reward(application_overall_rewards)
                cls._ode.get_statistics().add_failure_rate(application_failures)
                cls._ode.get_statistics().add_service_avail((offloading_attempts - application_failures) / offloading_attempts * 100)
                cls._ode.get_statistics().add_bandwidth_consumption(curr_bandwidth_consumption)
                cls.__reset_offloading_site_discrete_epoch_counters()

            cls._stats_log = cls._stats_log + (cls._ode, )

            print('##############################################################')
            print('################## ' + cls._ode.get_name() + ' OFFLOADING RESULT SUMMARY #################')
            print('################## ' + app_name + ' ###########################################')
            print('##############################################################\n')
            print("Time mean: " + str(cls._ode.get_statistics().get_time_completion_mean()) + ' s')
            print("Time variance: " + str(cls._ode.get_statistics().get_time_completion_var()) + ' s\n')
            print("Battery lifetime mean: " + str(cls._ode.get_statistics().get_energy_consumption_mean()) + '%')
            print("Battery lifetime variance: " + str(cls._ode.get_statistics().get_energy_consumption_var()) + '%\n')
            print("Offloading failure rate mean: " + str(cls._ode.get_statistics().get_failure_rates_mean()) + ' failures')
            print("Offloading failure rate variance: " + str(cls._ode.get_statistics().get_failure_rates_var()) + ' failures\n')
            print("Network bandwidth consumption mean: " + str(cls._ode.get_statistics().get_bandwidth_consumption_mean()) + " kbps")
            print("Network bandwidth consumption variance: " + str(cls._ode.get_statistics().get_bandwidth_consumption_var()) + " kbps\n")
            print("Service availability rate mean: " + str(cls._ode.get_statistics().get_service_avail_mean()) + "%")
            print("Service availability rate variance: " + str(cls._ode.get_statistics().get_service_avail_var()) + "%\n")
            print("Offloading distribution: " + \
                str(cls._ode.get_statistics().get_offloading_distribution()))
            print("Offloading distribution relative: " + \
                str(cls._ode.get_statistics().get_offloading_distribution_relative()))
            print("Num of offloadings: " + \
                str(cls._ode.get_statistics().get_num_of_offloadings()) + '\n')

            text = ""
            all_failures = 0
            for edge in cls._edge_servers:
                all_failures += edge.get_failure_cnt()
            text += edge.get_name() + ': ' + str(edge.get_failure_cnt()) + ', '

            all_failures += cls._cloud_dc.get_failure_cnt()
            text += cls._cloud_dc.get_name() + ': ' + str(cls._cloud_dc.get_failure_cnt())
            print("Failure frequency occurence: " + text)

            text = ""
            for edge in cls._edge_servers:
                text += edge.get_name() + ': ' + str(round(edge.get_failure_cnt() / all_failures * 100, 2)) + ', '

            text += cls._cloud_dc.get_name() + ': ' + str(round(cls._cloud_dc.get_failure_cnt() / all_failures * 100, 2))
            print("Relative failure frequency occurence: " + text)
            print("Num of failures: " + str(all_failures) + '\n')
            print("Offloading failure distribution: " + \
                str(cls._ode.get_statistics().get_offloading_failure_frequencies()))
            print("Offloading failure frequency relative: " + \
                str(cls._ode.get_statistics().get_offloading_failure_relative()))
            print("Num of offloading failures: " + \
                str(cls._ode.get_statistics().get_num_of_offloading_failures()) + '\n')
            print('Offloading site datasets:')
            for edge in cls._edge_servers:
                print(edge.get_name() + ' ' + str(edge.get_node_candidate()))

            print(cls._cloud_dc.get_name() + ' ' + str(cls._cloud_dc.get_node_candidate()))
