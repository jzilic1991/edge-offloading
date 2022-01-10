import math

from utilities import OffloadingActions, OdeType
from mdp_ode import MdpOde
from ode import OffloadingDecisionEngine


class EfpoOde(MdpOde):
    
    def __init__(self, mobile_device, edge_servers, cloud_dc, network, name):
        super().__init__(mobile_device, edge_servers, cloud_dc, network, name, OdeType.EFPO)


    def update_P_matrix(cls):
        for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS): 
            for j in range(math.ceil(cls._P[i].size / cls._P[i][0].size)): 
                for k in range(math.ceil(cls._P[i][j].size / cls._P[i][j][0].size)):
                    if cls._offloading_sites[k].get_offloading_action_index() == i:
                        cls._P[i][j][k] = 1 - cls._offloading_sites[k].\
                            get_fail_trans_prob(OdeType.EFPO) 

                    elif cls._mobile_device.get_offloading_action_index() == k:
                        cls._P[i][j][k] = cls._offloading_sites[i].\
                            get_fail_trans_prob(OdeType.EFPO)

                    else:
                        cls._P[i][j][k] = 0.0


    def update_R_matrix(cls, task, validity_vector):
        for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS): 
            for j in range(math.ceil(cls._R[i].size / cls._R[i][0].size)):
                for k in range(math.ceil(cls._R[i][j].size / cls._R[i][j][0].size)): 
                    if cls._P[i][j][k] == 0.0 or not validity_vector[i]:
                        cls._R[i][j][k] = 0.0
                        cls._response_time_matrix[i][j][k] = 0.0
                        continue

                    task_rsp_time = cls._OffloadingDecisionEngine__compute_complete_task_time_completion(task, \
                            cls._offloading_sites[k], cls._offloading_sites[j])
                    task_energy_consum = cls._OffloadingDecisionEngine__compute_complete_energy_consumption\
                            (task_rsp_time, cls._offloading_sites[k], cls._offloading_sites[j])
                    task_time_completion_reward = cls._OffloadingDecisionEngine__compute_task_time_completion_reward\
                            (task_rsp_time.get_task_overall())
                    task_energy_consumption_reward = cls._OffloadingDecisionEngine__compute_task_energy_consumption_reward\
                            (task_energy_consum.get_task_overall())
                    task_overall_reward = cls._OffloadingDecisionEngine__compute_overall_task_reward\
                            (task_time_completion_reward, task_energy_consumption_reward)

                    if task_rsp_time.get_task_overall() < 0 or task_rsp_time.get_downlink() < 0 or \
                            task_rsp_time.get_execution() < 0 or task_rsp_time.get_uplink() < 0 \
                            or task_energy_consum.get_task_overall() < 0 or task_time_completion_reward < 0 or \
                            task_energy_consumption_reward < 0 or task_overall_reward < 0:
                        raise ValueError("Some value is negative, leading to negative rewards!")

                    cls._R[i][j][k] = round(task_overall_reward, 3)
                    cls._response_time_matrix[i][j][k] = round(task_rsp_time.get_task_overall(), 3)


    def recovery_action(cls, validity_vector, action_index):
        for i in range(len(validity_vector)):
            if i == 0:
                validity_vector[i] = True
            else:
                validity_vector[i] = False
    
        return validity_vector
