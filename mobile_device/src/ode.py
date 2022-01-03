import math
import random
import math
import mdptoolbox
import mdptoolbox.example
import numpy as np
from abc import ABC, abstractmethod

from utilities import OffloadingSiteCode, OffloadingActions, ResponseTime, EnergyConsum
from base_off_site import BaseOffloadingSite
from statistics import Statistics


# constants for time (ms -> s) and data conversion (kb for data size and mbps for bandwdith)
KILOBYTE = 1000            # bytes
KILOBYTE_PER_SECOND = 1000 # 1Mbps -> 0.125 Mb/s
THOUSAND_MS = 1000         # 1000ms -> 1s used for network latency unit conversion
GIGABYTES = 1000000

# constans for power consumption (Watts)
POWER_CONSUM_UPLINK = 1.3
POWER_CONSUM_DOWNLINK = 1.0
POWER_CONSUM_LOCAL = 0.9
POWER_CONSUM_IDLE = 0.3

OFFLOADING_FAILURE_DETECTION_TIME = 1.5 # seconds


class OffloadingDecisionEngine(ABC):

    def __init__(self, mobile_device, edge_servers, cloud_dc, network, name):
        if not self.__evaluate_params(mobile_device, edge_servers, cloud_dc, network):
            raise ValueError("Wrong parameters passed to DummyOde object!")
    
        self._name = name
        self._mobile_device = mobile_device
        self._edge_servers = edge_servers
        self._cloud_dc = cloud_dc
        self._network = network
        self._offloading_sites = [None for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS)] 
        self._app_name = ""
        self._w_f_time_completion = 0.5
        self._w_f_energy_consumption = 0.5

        for edge_server in self._edge_servers:
            self._offloading_sites[edge_server.get_offloading_action_index()] = edge_server

        self._offloading_sites[self._mobile_device.get_offloading_action_index()] = self._mobile_device
        self._offloading_sites[self._cloud_dc.get_offloading_action_index()] = self._cloud_dc

        self._previous_node = self._mobile_device
        self._current_node = self._mobile_device

        self._statistics = Statistics (self._offloading_sites)

        self.initialize_params()
        super().__init__()


    def get_name(cls):
        return cls._name + "_t_" + str(cls._w_f_time_completion) + "_e_" + str(cls._w_f_energy_consumption)
    

    def get_statistics (cls):
        return cls._statistics


    @abstractmethod
    def initialize_params(cls):
        pass


    @abstractmethod
    def offload(cls, tasks):
        pass


    def __increment_discrete_epoch_counters(cls):
        for offloading_site in cls._offloading_sites:
            if offloading_site.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
                offloading_site.evaluate_failure_event()


    def __evaluate_params(cls, mobile_device, edge_servers, cloud_dc, network):
        if not isinstance(cloud_dc, BaseOffloadingSite):
            print("Cloud data center should be OffloadingSite object instance in ODE class!")
            return False

        if not edge_servers:
            print("Edge servers should not be empty in ODE class!")
            return False

        for edge in edge_servers:
            if not isinstance(edge, BaseOffloadingSite):
                print("Edge servers should be OffloadingSite object instance in ODE class!")
                return False

        if not (cloud_dc.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER):
            print("Cloud data center should be configured as cloud data center in ODE class!")
            return False

        for edge in edge_servers:
            if not (edge.get_offloading_site_code() in [OffloadingSiteCode.EDGE_DATABASE_SERVER, \
                OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER, OffloadingSiteCode.EDGE_REGULAR_SERVER]):
                print("Edge server should be configured as edge server in ODE class!")
                return False

        return True


    def __increment_discrete_epoch_counters(cls):
        for offloading_site in cls._offloading_sites:
            if offloading_site.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
                offloading_site.evaluate_failure_event()


    def __compute_bandwidth_consumption(cls, task, current_node, previous_node):
        if current_node.get_name() != previous_node.get_name():
            return (task.get_data_in() * KILOBYTE) / (cls.__get_network_bandwidth(current_node.get_name(), \
                    previous_node.get_name()) * KILOBYTE_PER_SECOND)

        return 0


    def __compute_complete_task_time_completion(cls, task, current_node, previous_node):
        if current_node.get_name() == previous_node.get_name():
            execution_time = cls.__compute_execution_time(task, current_node)
            # print ("Computed execution time is " + str(execution_time))
            return ResponseTime (execution_time, 0, 0, execution_time)
            # return (0, execution_time, 0, execution_time)

        uplink_time = cls.__compute_uplink_time(task, current_node, previous_node)
        execution_time = cls.__compute_execution_time(task, current_node)
    
        if not task.get_out_edges():
            downlink_time = cls.__compute_downlink_time(task, cls._mobile_device, current_node)
        
        else:
            downlink_time = 0
                
        return ResponseTime (execution_time, downlink_time, uplink_time, \
            uplink_time + execution_time + downlink_time)
        # return (uplink_time, execution_time, downlink_time, uplink_time + execution_time + downlink_time)


    def __compute_uplink_time(cls, task, current_node, previous_node):
        return ((task.get_data_in() * KILOBYTE) / (cls.__get_network_bandwidth(current_node.get_name(),\
                previous_node.get_name()) * KILOBYTE_PER_SECOND)) + (cls.__get_network_latency(current_node.get_name(), \
                previous_node.get_name()) / THOUSAND_MS)


    def __compute_downlink_time(cls, task, current_node, previous_node):
        if current_node.get_name() == previous_node.get_name():
            return 0.0

        return ((task.get_data_out() * KILOBYTE) / (cls.__get_network_bandwidth(current_node.get_name(), \
                previous_node.get_name()) * KILOBYTE_PER_SECOND)) + (cls.__get_network_latency(current_node.get_name(), \
                previous_node.get_name()) / THOUSAND_MS)


    def __compute_execution_time(cls, task, current_node):
        return task.get_millions_of_instructions() / current_node.get_millions_of_instructions_per_second()


    def __compute_complete_energy_consumption(cls, task_rsp_time, current_node, previous_node):
        uplink_time_power = 0.0
        execution_time_power = 0.0
        downlink_time_power = 0.0
        task_energy_consumption = 0.0

        execution_time = task_rsp_time.get_execution()
        downlink_time = task_rsp_time.get_downlink()
        uplink_time = task_rsp_time.get_uplink()
    
        if current_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and\
            previous_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
            execution_time_power = cls.__compute_execution_energy_consumption(execution_time)
            task_energy_consumption = uplink_time_power + execution_time_power + downlink_time_power

        # use case: mobile device -> Edge/Cloud servers
        elif current_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and\
            previous_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
            uplink_time_power = cls.__compute_uplink_energy_consumption(uplink_time)
            execution_time_power = cls.__compute_idle_energy_consumption(execution_time)
            downlink_time_power = cls.__compute_downlink_energy_consumption(downlink_time)
            task_energy_consumption = cls.__compute_offloading_energy_consumption_uplink_direction\
                    (uplink_time, execution_time, downlink_time)

        # use case: Cloud/Edge -> Cloud/Edge (successive tasks executed on the same node)
        elif current_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and\
            previous_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and\
            current_node.get_name() == previous_node.get_name():
            execution_time_power = cls.__compute_idle_energy_consumption(execution_time)
            downlink_time_power = cls.__compute_downlink_energy_consumption(downlink_time)
            task_energy_consumption = cls.__compute_energy_consumption_during_remote_execution(execution_time, downlink_time)

        # use case: Cloud/Edge -> Cloud/Edge (successive tasks executed on the different nodes)	
        elif current_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and\
            previous_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and\
            current_node.get_name() != previous_node.get_name():
            execution_time_power = cls.__compute_idle_energy_consumption(uplink_time + execution_time)
            downlink_time_power = cls.__compute_downlink_energy_consumption(downlink_time)
            task_energy_consumption = cls.__compute_energy_consumption_during_remote_execution\
                    (uplink_time + execution_time, downlink_time)

        # use case: Cloud/Edge -> mobile device
        elif current_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and\
            previous_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
            execution_time_power = cls.__compute_execution_energy_consumption(execution_time)
            downlink_time_power = cls.__compute_downlink_energy_consumption(uplink_time)
            task_energy_consumption = cls.__compute_offloading_energy_consumption_downlink_direction(uplink_time, execution_time)

        return EnergyConsum (execution_time_power, downlink_time_power, uplink_time_power, task_energy_consumption)
        #return (uplink_time_power, execution_time_power, downlink_time_power, task_energy_consumption)


    def __compute_failure_cost(cls, candidate_node, previous_node):
        cost_rsp_time = ResponseTime (OFFLOADING_FAILURE_DETECTION_TIME, 0.0, 0.0, OFFLOADING_FAILURE_DETECTION_TIME)
        cost_energy_consum = EnergyConsum (0.0, 0.0, 0.0, 0.0)
        cost_rewards = 0

        if candidate_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and \
            previous_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
            task_rsp_time = ResponseTime (time_cost, 0.0, 0.0, time_cost)
            cost_energy_consum = cls.__compute_complete_energy_consumption(task_rsp_time, candidate_node, previous_node)
            task_time_reward = cls.__compute_task_time_completion_reward(time_cost.get_task_overall())
            task_energy_reward = cls.__compute_task_energy_consumption_reward(cost_energy_consum.get_task_overall())
            cost_rewards = cls.__compute_overall_task_reward(task_time_reward, task_energy_reward)

        elif candidate_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and \
            previous_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
            task_rsp_time = ResponseTime (0.0, time_cost, 0.0, time_cost)
            cost_energy_consum = cls.__compute_complete_energy_consumption(task_rsp_time, candidate_node, previous_node)
            task_time_reward = cls.__compute_task_time_completion_reward(task_rsp_time.get_task_overall())
            task_energy_reward = cls.__compute_task_energy_consumption_reward(energy_consum.get_task_overall())
            cost_rewards = cls.__compute_overall_task_reward(task_time_reward, task_energy_reward)

        elif candidate_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and \
            previous_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
            task_rsp_time = ResponseTime (0.0, 0.0, time_cost, time_cost)
            cost_energy_consum = cls.__compute_complete_energy_consumption(task_rsp_time, 0.0, 0.0, candidate_node, previous_node)
            task_time_reward = cls.__compute_task_time_completion_reward(task_rsp_time.get_task_overall())
            task_energy_reward = cls.__compute_task_energy_consumption_reward(cost_energy_consum.get_task_overall())
            cost_rewards = cls.__compute_overall_task_reward(task_time_reward, task_energy_reward)

        return (cost_rsp_time, cost_energy_consum, cost_rewards)


    def __compute_offloading_energy_consumption_downlink_direction(cls, downlink_time, execution_time):
        return cls.__compute_downlink_energy_consumption(downlink_time) + cls.__compute_execution_energy_consumption(execution_time)

    
    def __compute_offloading_energy_consumption_uplink_direction(cls, uplink_time, idle_time, downlink_time):
        return cls.__compute_uplink_energy_consumption(uplink_time) + cls.__compute_idle_energy_consumption(idle_time) \
            + cls.__compute_downlink_energy_consumption(downlink_time)
    
    
    def __compute_energy_consumption_during_remote_execution(cls, remote_execution_time, downlink_time):
        return cls.__compute_idle_energy_consumption(remote_execution_time) + cls.__compute_downlink_energy_consumption(downlink_time)

    
    def __compute_uplink_energy_consumption(cls, uplink_time):
        return uplink_time * POWER_CONSUM_UPLINK


    def __compute_downlink_energy_consumption(cls, downlink_time):
        return downlink_time * POWER_CONSUM_DOWNLINK


    def __compute_execution_energy_consumption(cls, execution_time):
        return execution_time * POWER_CONSUM_LOCAL

    
    def __compute_idle_energy_consumption(cls, idle_time):
        return idle_time * POWER_CONSUM_IDLE

    
    def __compute_task_time_completion_reward(cls, task_completion_time):
        if task_completion_time == 0.0:
            return 0.0

        return 1 / (1 + math.exp(task_completion_time))


    def __compute_task_energy_consumption_reward(cls, task_energy_consumption):
        if task_energy_consumption == 0.0:
            return 0.0

        return 1 / (1 + math.exp(task_energy_consumption))

    
    def __compute_overall_task_reward(cls, time_reward, energy_reward):
        return (cls._w_f_time_completion * time_reward) + \
                (cls._w_f_energy_consumption * energy_reward)
    
    
    def __get_network_latency(cls, current_node_name, previous_node_name):
        if current_node_name == previous_node_name:
            return 0.0

        for value in cls._network[previous_node_name]:
            if value[0] == current_node_name:
                return value[1]

        raise ValueError("Cannot find network latency between " + current_node_name + " and " + previous_node_name)


    def __get_network_bandwidth(cls, current_node_name, previous_node_name):
        if current_node_name == previous_node_name:
            return 0.0

        for value in cls._network[previous_node_name]:
            if value[0] == current_node_name:
                return value[2]

        raise ValueError("Cannot find network bandwidth between " + current_node_name + " and " + previous_node_name)
