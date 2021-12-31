import math

from utilities import OffloadingActions, OffloadingSiteCode, OdeType
from ode import OffloadingDecisionEngine
from mdp_ode import MdpOde
from logger import Logger


class MdpSvrOde(MdpOde):

    def initialize_params(cls):
        cls._MdpOde__init_MDP_settings()
        cls._discount_factor = 0.01


    def update_P_matrix(cls):
        # Logger.w('####################################################################')
        # Logger.w('########################## ' + cls._name +' PROBABILITY MATRIX ############################')
        # Logger.w('####################################################################\n')
        # Logger.w('Current offloading position: ' + cls._current_node.get_name() + '\n')

        for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS): 
            for j in range(math.ceil(cls._P[i].size / cls._P[i][0].size)):
                for k in range(math.ceil(cls._P[i][j].size / cls._P[i][j][0].size)): 
                    
                    # offload to k offloading site
                    if cls._offloading_sites[k].get_offloading_action_index() == i:
                        cls._P[i][j][k] = 1 - cls._offloading_sites[k].\
                            get_fail_trans_prob() #OdeType.MDP_SVR as a argument

                    # offload to mobile device (in case of offloading failure) 
                    elif cls._mobile_device.get_offloading_action_index() == k:
                        cls._P[i][j][k] = cls._offloading_sites[i].\
                            get_fail_trans_prob() # OdeType.MDP_SVR as a argument

                    else:
                        cls._P[i][j][k] = 0.0

                #cls.__check_stochasticity_of_P_matrix(i, j)

            # Logger.w(cls._offloading_sites[i].get_name() + ' updated P matrix: ' + \
            #    str(cls._P[i]) + '\n')


    def update_R_matrix(cls, task, validity_vector):
        # print ('####################################################################')
        # print ('########################## ' + cls._name +' RESPONSE TIME MATRIX ############################')
        # print ('####################################################################\n')
        # print ('Current offloading position: ' + cls._current_node.get_name() + '\n')

        for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS):
            for j in range(math.ceil(cls._R[i].size / cls._R[i][0].size)): 
                for k in range(math.ceil(cls._R[i][j].size / cls._R[i][j][0].size)):
                    if cls._P[i][j][k] == 0.0 or not validity_vector[i]:
                        cls._R[i][j][k] = 0.0
                        cls._response_time_matrix[i][j][k] = 0.0
                        continue

                    # print(cls._offloading_sites[j].get_name() + " -> " + cls._offloading_sites[k].get_name())
                    task_rsp_time = cls._OffloadingDecisionEngine__compute_complete_task_time_completion(task, \
                            cls._offloading_sites[k], cls._offloading_sites[j])
                    # print("Uplink time: " + str(task_rsp_time.get_uplink()))
                    # print("Execution time: " + str(task_rsp_time.get_execution()))
                    # print("Downlink time: " + str(task_rsp_time.get_downlink()))
                    # print("Task completion time: " + str(task_rsp_time.get_task_overall()) + "\n")

                    # compute task energy consumption
                    task_energy_consum = cls._OffloadingDecisionEngine__compute_complete_energy_consumption\
                            (task_rsp_time, cls._offloading_sites[k], cls._offloading_sites[j])
                    # print("Uplink energy: " + str(task_energy_consum.get_uplink()))
                    # print("Execution energy: " + str(task_energy_consum.get_execution()))
                    # print("Downlink energy: " + str(task_energy_consum.get_downlink()))
                    # print("Task energy: " + str(task_energy_consum.get_task_overall())+ "\n")

                    # compute task time completion reward
                    task_time_completion_reward = cls._OffloadingDecisionEngine__compute_task_time_completion_reward\
                            (task_rsp_time.get_task_overall())
                    # print("Task time completion reward: " + str(task_time_completion_reward))

                    # compute task energy reward
                    task_energy_consumption_reward = cls._OffloadingDecisionEngine__compute_task_energy_consumption_reward\
                            (task_energy_consum.get_task_overall())
                    # print("Task energy reward: " + str(task_energy_consumption_reward))

                    # compute task overall reward
                    task_overall_reward = cls._OffloadingDecisionEngine__compute_overall_task_reward\
                            (task_time_completion_reward, task_energy_consumption_reward)
                    # print("Task overall reward: " + str(task_overall_reward)+ "\n")

                    if task_rsp_time.get_task_overall() < 0 or task_rsp_time.get_downlink() < 0 or \
                            task_rsp_time.get_execution() < 0 or task_rsp_time.get_uplink() < 0 \
                            or task_energy_consum.get_task_overall() < 0 or task_time_completion_reward < 0 or \
                            task_energy_consumption_reward < 0 or task_overall_reward < 0:
                        raise ValueError("Some value is negative, leading to negative rewards!")

                    cls._R[i][j][k] = round(task_overall_reward, 3)
                    cls._response_time_matrix[i][j][k] = round(task_rsp_time.get_task_overall(), 3)

                    # Logger.w(cls._offloading_sites[i].get_name() + ' updated response time matrix: \n' + \
                    #   str(cls._response_time_matrix[i]) + '\n')

                # Logger.w('####################################################################')
                # Logger.w('########################## ' + cls._name +' REWARD MATRIX ############################')
                # Logger.w('####################################################################\n')

                # Logger.w('Current offloading position: ' + cls._current_node.get_name() + '\n')
                # for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS):
                #     Logger.w(cls._offloading_sites[i].get_name() + ' updated R matrix: \n' + \
                #        str(cls._R[i]) + '\n')


    def recovery_action(cls, validity_vector, action_index):
        validity_vector[action_index] = False
        return validity_vector


    def __check_stochasticity_of_P_matrix(cls, i, j):
        sum_probabilities = 0
        first_index = -1

        for k in range(math.ceil(cls._P[i][j].size / cls._P[i][j][0].size)):
            if cls._P[i][j][k] == 0:
                continue
    
            if first_index == -1:
                first_index = k

                sum_probabilities += cls._P[i][j][k]

            if sum_probabilities > 1:
                diff = sum_probabilities - 1
                cls._P[i][j][first_index] -= diff
                cls._P[i][j][first_index] = float('{:.2f}'.format(cls._P[i][j][first_index]))

            elif sum_probabilities < 1:
                diff = 1 - sum_probabilities
                cls._P[i][j][first_index] += diff
                cls._P[i][j][first_index] = float('{:.2f}'.format(cls._P[i][j][first_index]))
