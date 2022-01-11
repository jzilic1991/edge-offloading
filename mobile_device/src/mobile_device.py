import datetime

from utilities import Util, NodeType, OffloadingSiteCode, OffloadingActions, ExecutionErrorCode
from resource_monitor import ResourceMonitor
from mob_app_profiler import MobileAppProfiler
from mdp_svr_ode import MdpSvrOde
from efpo_ode import EfpoOde
from task import Task
from logger import Logger

# constants
GIGABYTES = 1000000
PROGRESS_REPORT_INTERVAL = 1

FACEBOOK = "FACEBOOK"
FACERECOGNIZER = "FACERECOGNIZER"
CHESS = "CHESS"
ANTIVIRUS = "ANTIVIRUS"
GPS_NAVIGATOR = "GPS_NAVIGATOR"

LOCAL_ODE_NAME = "LOCAL"
MC_ODE_NAME = "MC"
EE_ODE_NAME = "EE"
EFPO_ODE_NAME = "EFPO"
MDP_SVR_ODE_NAME = "MDP_SVR"
CHECK_ODE_NAME = "CHECKPOINTING"
LOCAL_REEXE_ODE_NAME = "LOCAL_REEXECUTION"
REACTIVE_ODE_NAME = "REACTIVE"


class MobileDevice:

    def __init__(self, mips, memory, data_storage):
        self._mips = mips
        self._memory = memory
        self._data_storage = data_storage
    
        self._mobile_app = None
        self._ode = None
        self._res_monitor = ResourceMonitor (self)
        #self._edge_servers = self._res_monitor.get_edge_servers ()
        #self._cloud_dc = self._res_monitor.get_cloud_dc ()
        self._memory_consumption = 0
        self._data_storage_consumption = 0
        self._name = "MOBILE_DEVICE"
        self._offloading_site_code = OffloadingSiteCode.MOBILE_DEVICE
        self._offloading_action_index = OffloadingActions.MOBILE_DEVICE
        self._node_type = NodeType.MOBILE
        self._energy_supply_budget = 34200
        self._mobile_app_profiler = MobileAppProfiler ()
        self._mobile_app = None
        self._stats_hist = list ()
        self._network = self.__deploy_network_model ()
        self._log = Logger('logs/simulation.txt', True, 'w')
        self._init_run = True


    def get_offloading_site_code (cls):
        return cls._offloading_site_code


    def get_name (cls):
        return cls._name


    def get_node_type (cls):
        return cls._node_type
    
    
    def get_offloading_action_index (cls):
        return cls._offloading_action_index


    def get_millions_of_instructions_per_second (cls):
        return cls._mips
    

    def get_fail_trans_prob (cls, ode_type, t = 0):
        return 0.0


    def get_actual_fail_prob (cls):
        return 0.0


    def next_node_candidates (cls):
        cls._res_monitor.next_node_candidates()


    def update_fail_event (cls, event):
        pass


    def get_fail_event (cls):
        return None
    
    
    def execute(cls, task):
        print_text = "Task "

        if not isinstance(task, Task):
            print ("Task for execution on offloading site should be Task class instance!")
            return ExecutionErrorCode.EXE_NOK

        if not task.execute():
            return ExecutionErrorCode.EXE_NOK

        print_text = print_text + task.get_name()
        task_data_storage_consumption = task.get_data_in() + task.get_data_out()
        task_memory_consumption = task.get_memory()

        cls._data_storage_consumption = cls._data_storage_consumption + (task_data_storage_consumption / GIGABYTES)
        cls._memory_consumption = cls._memory_consumption + task_memory_consumption

        return ExecutionErrorCode.EXE_OK


    def print_system_config(cls):
        print ("################### MOBILE DEVICE SYSTEM CONFIGURATION ###################")
        print ("CPU: " + str(cls._mips) + " M cycles")
        print ("Memory: " + str(cls._memory) + " Gb")
        print ("Data Storage: " + str(cls._data_storage) + " Gb")
        print ('\n\n')


    def deploy_mdp_svr_ode (cls):
        cls._ode = MdpSvrOde(cls, cls._res_monitor.get_edge_servers (), cls._res_monitor.get_cloud_dc (), \
                cls._network, MDP_SVR_ODE_NAME)
    

    def deploy_efpo_ode (cls):
        cls._ode = EfpoOde(cls, cls._res_monitor.get_edge_servers (), cls._res_monitor.get_cloud_dc (), \
                cls._network, EFPO_ODE_NAME)


    def run(cls, samplings, executions):
        if not cls._ode:
            return ExecutionErrorCode.EXE_NOK

        if not cls._init_run:
            cls._log.update_action('a')
        
        previous_progress = 0
        current_progress = 0
        # cls._ode.get_statistics() = Statistics (cls._res_monitor.get_off_sites ())

        print ("**************** PROGRESS with " + cls._ode.get_name() + "****************")
        print (str(previous_progress) + "% - " + str(datetime.datetime.utcnow()))

        for i in range(samplings):
            application_time_completion = 0
            application_energy_consumption = 0
            application_overall_rewards = 0 
            application_fail_time_completion = 0
            application_fail_energy_consumption = 0
            application_failures = 0
            offloading_attempts = 0

            # reset test data after each simulation sampling to start from the beginning
            cls._res_monitor.reset_test_data ()

            # simulate application executions   
            for j in range(executions):
                single_app_exe_task_comp = 0
                single_app_exe_energy_consum = 0
                previous_progress = current_progress
                current_progress = round((j + (i * executions)) / (samplings * executions) * 100)

                if current_progress != previous_progress and (current_progress % PROGRESS_REPORT_INTERVAL == 0):
                    print(str(current_progress) + "% - " + str(datetime.datetime.utcnow()))

                cls._mobile_app = cls._mobile_app_profiler.deploy_random_mobile_app()
                # cls._mobile_app.print_entire_config()
                cls._mobile_app.run()
               
                # Logger.w (cls._mobile_app.get_name() + ' application is deployed!')
                ready_tasks = cls._mobile_app.get_ready_tasks()
                
                while ready_tasks:
                    (task_completion_time, task_energy_consumption, task_overall_reward, task_failure_time_cost,\
                            task_failure_energy_cost, task_failures) = cls._ode.offload(ready_tasks)
                    offloading_attempts += task_failures + len(ready_tasks)
                    # print ("Failed offloading attemps: " + str(task_failures))
                    # print ("Successful offloading attempts:" + str(len(ready_tasks)))
                    # print ("Current offloading attempts: " + str(offloading_attempts))
                    ready_tasks = cls._mobile_app.get_ready_tasks()

                    application_time_completion = round(application_time_completion + task_completion_time, 3)
                    application_fail_time_completion += round(task_failure_time_cost, 3)
                    single_app_exe_task_comp = round(single_app_exe_task_comp + task_completion_time, 3)
                    # Logger.w ("Current application runtime: " + str(application_time_completion) + " s")

                    application_energy_consumption = round(application_energy_consumption + task_energy_consumption, 3)
                    application_fail_energy_consumption = round(application_fail_energy_consumption + task_failure_energy_cost, 3)
                    single_app_exe_energy_consum = round(single_app_exe_energy_consum + task_energy_consumption, 3)
                    # Logger.w ("Current application energy consumption: " + str(application_energy_consumption) + " J")

                    application_failures += task_failures
                    # Logger.w ("Current application failures: " + str(application_failures) + '\n')

                    application_overall_rewards = round(application_overall_rewards + task_overall_reward, 3)
                    
                    # increment new time epoch for next availability sample and failure event evaluation
                    cls._ode.count_time_epoch()

                    # curr_bandwidth_consumption += epoch_bandwidth_consumption

                    # print ("Current application overall rewards: " + str(application_overall_rewards))
                    # print ("Current bandwidth consumption: " + str(curr_bandwidth_consumption) + ' kbps\n')
                    # print ('Task application runtime: ' + str(task_completion_time) + 's')
                    # print ('Task energy consumption: ' + str(task_energy_consumption) + 'J')
                    # print ('Task rewards: ' + str(task_overall_reward))
                    # print ('Task failure time cost:' + str(task_failure_time_cost) + 's')

                    # cls._mobile_app.print_task_exe_status()

                # cls.__reset_application()
                cls._ode.get_statistics().add_time_comp_single_app_exe(single_app_exe_task_comp)
                cls._ode.get_statistics().add_energy_consum_single_app_exe(single_app_exe_energy_consum)
                
            cls._ode.get_statistics().add_time_comp(application_time_completion)
                    
            battery_lifetime = (cls._energy_supply_budget - application_energy_consumption) / cls._energy_supply_budget * 100
            cls._ode.get_statistics().add_energy_eff(battery_lifetime)
            cls._ode.get_statistics().add_reward(application_overall_rewards)
            cls._ode.get_statistics().add_failure_rate(application_failures)
            cls._ode.get_statistics().add_service_avail((offloading_attempts - application_failures) / offloading_attempts * 100)
            # cls._ode.get_statistics().add_bandwidth_consumption(curr_bandwidth_consumption)
            # cls.__reset_offloading_site_discrete_epoch_counters()

        cls._stats_hist.append (cls._ode.get_statistics())
        cls.__print_log_results ()
        
        cls._ode.get_statistics().reset_stats()
        cls._init_run = False


    def __print_log_results (cls):
        # print ('Get all time completion: ' + str(cls._ode.get_statistics().get_all_time_comp()))
        # print ('Get all battery lifetime: '  + str(cls._ode.get_statistics().get_all_energy_consum()))
        # print ('Get all service availability: ' + str(cls._ode.get_statistics().get_all_service_avail()))

        cls._log.p('##############################################################')
        cls._log.p('################## ' + cls._ode.get_name() + ' OFFLOADING RESULT SUMMARY #################')
        # print('################## ' + app_name + ' ###########################################')
        cls._log.p('##############################################################\n')
        cls._log.p("Time mean: " + str(cls._ode.get_statistics().get_time_completion_mean()) + ' s')
        cls._log.p("Time variance: " + str(cls._ode.get_statistics().get_time_completion_var()) + ' s\n')
        cls._log.p("Battery lifetime mean: " + str(cls._ode.get_statistics().get_energy_consumption_mean()) + '%')
        cls._log.p("Battery lifetime variance: " + str(cls._ode.get_statistics().get_energy_consumption_var()) + '%\n')
        cls._log.p("Offloading failure rate mean: " + str(cls._ode.get_statistics().get_failure_rates_mean()) + ' failures')
        cls._log.p("Offloading failure rate variance: " + str(cls._ode.get_statistics().get_failure_rates_var()) + ' failures\n')
        # print("Network bandwidth consumption mean: " + str(cls._ode.get_statistics().get_bandwidth_consumption_mean()) + " kbps")
        # print("Network bandwidth consumption variance: " + str(cls._ode.get_statistics().get_bandwidth_consumption_var()) + " kbps\n")
        cls._log.p("Service availability rate mean: " + str(cls._ode.get_statistics().get_service_avail_mean()) + "%")
        cls._log.p("Service availability rate variance: " + str(cls._ode.get_statistics().get_service_avail_var()) + "%\n")
        cls._log.p("Offloading distribution: " + \
            str(cls._ode.get_statistics().get_offloading_distribution()))
        cls._log.p("Offloading distribution relative: " + \
            str(cls._ode.get_statistics().get_offloading_distribution_relative()))
        cls._log.p("Num of offloadings: " + \
            str(cls._ode.get_statistics().get_num_of_offloadings()) + '\n')
        
        cls._log.p("Failure frequency occurence: " + str(cls._ode.get_statistics().get_failure_events()))
        cls._log.p("Relative failure frequency occurence: " + str(cls._ode.get_statistics().get_failure_events_relative()))
        cls._log.p("Num of failures: " + str(cls._ode.get_statistics().get_num_of_failure_events()) + '\n')
        
        # text = ""
        # all_failures = 0
        # for edge in cls._res_monitor.get_edge_servers():
        #    all_failures += edge.get_failure_cnt()
        #    text += edge.get_name() + ': ' + str(edge.get_failure_cnt()) + ', '

        # all_failures += cls._res_monitor.get_cloud_dc().get_failure_cnt()
        # text += cls._res_monitor.get_cloud_dc().get_name() + ': ' + str(cls._res_monitor.get_cloud_dc().get_failure_cnt())
        # cls._log.p("Failure frequency occurence: " + text)

        # text = ""
        # for edge in cls._res_monitor.get_edge_servers():
        #    text += edge.get_name() + ': ' + str(round(edge.get_failure_cnt() / all_failures * 100, 2)) + ', '

        # text += cls._res_monitor.get_cloud_dc().get_name() + ': ' + \
        #        str(round(cls._res_monitor.get_cloud_dc().get_failure_cnt() / all_failures * 100, 2))
        # cls._log.p("Relative failure frequency occurence: " + text)
        # cls._log.p("Num of failures: " + str(all_failures) + '\n')

        cls._log.p("Offloading failure distribution: " + \
            str(cls._ode.get_statistics().get_offloading_failure_frequencies()))
        cls._log.p("Offloading failure frequency relative: " + \
            str(cls._ode.get_statistics().get_offloading_failure_relative()))
        cls._log.p("Num of offloading failures: " + \
            str(cls._ode.get_statistics().get_num_of_offloading_failures()) + '\n')
        
   

    def __deploy_network_model (cls):
        cloud_dc = cls._res_monitor.get_cloud_dc()
        edge_db_server = cls._res_monitor.get_edge_dat_server()
        edge_comp_server = cls._res_monitor.get_edge_comp_server()
        edge_reg_server = cls._res_monitor.get_edge_reg_server()
        mobile_device = cls

        # Cloud DC <-> Edge database server
        cloud_dc__edge_db_server__net_lat = Util.get_network_latency(cloud_dc, edge_db_server)

        # Cloud DC <-> Edge computational intensive server
        cloud_dc__edge_comp_server__net_lat = Util.get_network_latency(cloud_dc, edge_comp_server)

        # Cloud DC <-> Edge regular server
        cloud_dc__edge_reg_server__net_lat = Util.get_network_latency(cloud_dc, edge_reg_server)

        # Cloud DC <-> mobile device
        cloud_dc__mobile_device__net_lat = Util.get_network_latency(cloud_dc, mobile_device)

        # Edge database server <-> Edge computational intensive server
        edge_db_server__edge_comp_server__net_lat = Util.get_network_latency(edge_db_server, edge_comp_server)

        # Edge database server <-> Edge regular server
        edge_db_server__edge_reg_server__net_lat = Util.get_network_latency(edge_db_server, edge_reg_server)

        # Edge database server <-> mobile device
        edge_db_server__mobile_device__net_lat = Util.get_network_latency(edge_db_server, mobile_device)

        # Edge computational intensive server <-> Edge regular server
        edge_comp_server__edge_reg_server__net_lat = Util.get_network_latency(edge_comp_server, edge_reg_server)

        # Edge computational intensive server <-> mobile device
        edge_comp_server__mobile_device__net_lat = Util.get_network_latency(edge_comp_server, mobile_device)

        # Edge regular server <-> mobile device
        edge_reg_server__mobild_device__net_lat = Util.get_network_latency(edge_reg_server, mobile_device)


        return {
            cloud_dc.get_name(): [(edge_db_server.get_name(), cloud_dc__edge_db_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(cloud_dc, edge_db_server)), \
                    (edge_comp_server.get_name(), cloud_dc__edge_comp_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(cloud_dc, edge_comp_server)),\
                    (edge_reg_server.get_name(), cloud_dc__edge_reg_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(cloud_dc, edge_reg_server)), \
                    (mobile_device.get_name(), cloud_dc__mobile_device__net_lat, \
                    cls._res_monitor.get_network_bandwidth(cloud_dc, mobile_device))],
            edge_db_server.get_name(): [(cloud_dc.get_name(), cloud_dc__edge_db_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_db_server, cloud_dc)),\
                    (edge_comp_server.get_name(), edge_db_server__edge_comp_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_db_server, edge_comp_server)),\
                    (edge_reg_server.get_name(), edge_db_server__edge_reg_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_db_server, edge_reg_server)),\
                    (mobile_device.get_name(), edge_db_server__mobile_device__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_db_server, mobile_device))],
            edge_comp_server.get_name(): [(cloud_dc.get_name(), cloud_dc__edge_comp_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_comp_server, cloud_dc)),\
                    (edge_db_server.get_name(), edge_db_server__edge_comp_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_comp_server, edge_db_server)),\
                    (edge_reg_server.get_name(), edge_comp_server__edge_reg_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_comp_server, edge_reg_server)),\
                    (mobile_device.get_name(), edge_comp_server__mobile_device__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_comp_server, mobile_device))],
            edge_reg_server.get_name(): [(cloud_dc.get_name(), cloud_dc__edge_reg_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_reg_server, cloud_dc)),\
                    (edge_db_server.get_name(), edge_db_server__edge_reg_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_reg_server, edge_db_server)),\
                    (edge_comp_server.get_name(), edge_comp_server__edge_reg_server__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_reg_server, edge_comp_server)),\
                    (mobile_device.get_name(), edge_reg_server__mobild_device__net_lat, \
                    cls._res_monitor.get_network_bandwidth(edge_reg_server, mobile_device))],
            mobile_device.get_name(): [(cloud_dc.get_name(), cloud_dc__mobile_device__net_lat, \
                    cls._res_monitor.get_network_bandwidth(mobile_device, cloud_dc)),\
                    (edge_db_server.get_name(), edge_db_server__mobile_device__net_lat, \
                    cls._res_monitor.get_network_bandwidth(mobile_device, edge_db_server)),\
                    (edge_comp_server.get_name(), edge_comp_server__mobile_device__net_lat, \
                    cls._res_monitor.get_network_bandwidth(mobile_device, edge_comp_server)),
                    (edge_reg_server.get_name(), edge_reg_server__mobild_device__net_lat, \
                    cls._res_monitor.get_network_bandwidth(mobile_device, edge_reg_server))]}
    
    
    def check_validity_of_deployment(cls, task):
        if not isinstance(task, Task):
            print ("Task for execution on offloading site should be Task class instance!")
            return ExecutionErrorCode.EXE_NOK

        if cls._data_storage > (cls._data_storage_consumption + ((task.get_data_in() + task.get_data_out())) / GIGABYTES) and \
            cls._memory > (cls._memory_consumption + task.get_memory()):
            return ExecutionErrorCode.EXE_OK
    
        return ExecutionErrorCode.EXE_NOK


    def terminate_task(cls, task):
        if not isinstance(task, Task):
            print ("Task for execution on offloading site should be Task class instance!")
            return ExecutionErrorCode.EXE_NOK
    
        cls._memory_consumption = cls._memory_consumption - task.get_memory()
        cls._data_storage_consumption = cls._data_storage_consumption - ((task.get_data_in() + task.get_data_out()) / GIGABYTES)

        if cls._memory_consumption < 0 or cls._data_storage_consumption < 0:
            raise ValueError("Memory consumption: " + str(cls._memory_consumption) + \
                    "Gb, data storage consumption: " + str(cls._data_storage_consumption) + \
                    "Gb, both should be positive! Node: " + cls._name + ", task: " + task.get_name())
