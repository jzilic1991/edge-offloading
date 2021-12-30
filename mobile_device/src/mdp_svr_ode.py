import math

from utilities import OffloadingActions, OffloadingSiteCode, OdeType
from ode import OffloadingDecisionEngine
from mdp_ode import MdpOde


class MdpSvrOde(MdpOde):

    def initialize_params(cls):
        cls._MdpOde__init_MDP_settings()

        cls._discount_factor = 0.01

        #for offloading_site in cls._offloading_sites:
        #    if offloading_site.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
        #        offloading_site.deploy_svr()


    def update_P_matrix(cls):
        print ('####################################################################')
        print ('########################## ' + cls._name +' PROBABILITY MATRIX ############################')
        print ('####################################################################\n')
        print ('Current offloading position: ' + cls._current_node.get_name() + '\n')

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

                cls.__check_stochasticity_of_P_matrix(i, j)

            print(cls._offloading_sites[i].get_name() + ' updated P matrix: ' + \
                str(cls._P[i]) + '\n')


    def update_R_matrix(cls, task, validity_vector):
        print ('####################################################################')
        print ('########################## ' + cls._name +' RESPONSE TIME MATRIX ############################')
        print ('####################################################################\n')
        print ('Current offloading position: ' + cls._current_node.get_name() + '\n')

        for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS):
            for j in range(math.ceil(cls._R[i].size / cls._R[i][0].size)): 
                for k in range(math.ceil(cls._R[i][j].size / cls._R[i][j][0].size)):
                    if cls._P[i][j][k] == 0.0 or not validity_vector[i]:
                        cls._R[i][j][k] = 0.0
                        cls._response_time_matrix[i][j][k] = 0.0
                        continue

                    print(cls._offloading_sites[j].get_name() + " -> " + cls._offloading_sites[k].get_name())
                    (uplink_time, execution_time, downlink_time, task_completion_time) = \
                            cls._OffloadingDecisionEngine__compute_complete_task_time_completion(task, \
                            cls._offloading_sites[k], cls._offloading_sites[j])
                    print("Uplink time: " + str(uplink_time))
                    print("Execution time: " + str(execution_time))
                    print("Downlink time: " + str(downlink_time))
                    print("Task completion time: " + str(task_completion_time)+ "\n")

                    # compute task energy consumption
                    (uplink_energy, execution_energy, downlink_energy, task_energy_consumption) = \
                        cls._OffloadingDecisionEngine__compute_complete_energy_consumption(uplink_time, \
                        execution_time, downlink_time, cls._offloading_sites[k], cls._offloading_sites[j])
                    print("Uplink energy: " + str(uplink_energy))
                    print("Execution energy: " + str(execution_energy))
                    print("Downlink energy: " + str(downlink_energy))
                    print("Task energy: " + str(task_energy_consumption)+ "\n")

                    # compute task time completion reward
                    task_time_completion_reward = cls._OffloadingDecisionEngine__compute_task_time_completion_reward\
                            (task_completion_time)
                    print("Task time completion reward: " + str(task_time_completion_reward))

                    # compute task energy reward
                    task_energy_consumption_reward = cls._OffloadingDecisionEngine__compute_task_energy_consumption_reward\
                            (task_energy_consumption)
                    print("Task energy reward: " + str(task_energy_consumption_reward))

                    # compute task overall reward
                    task_overall_reward = cls._OffloadingDecisionEngine__compute_overall_task_reward\
                            (task_time_completion_reward, task_energy_consumption_reward)
                    print("Task overall reward: " + str(task_overall_reward)+ "\n")

                    if task_completion_time < 0 or downlink_time < 0 or execution_time < 0 or uplink_time < 0 \
                            or task_energy_consumption < 0 or task_time_completion_reward < 0 or \
                            task_energy_consumption_reward < 0 or task_overall_reward < 0:
                        raise ValueError("Some value is negative, leading to negative rewards!")

                    cls._R[i][j][k] = round(task_overall_reward, 3)
                    cls._response_time_matrix[i][j][k] = round(task_completion_time, 3)

                    print(cls._offloading_sites[i].get_name() + ' updated response time matrix: \n' + \
                       str(cls._response_time_matrix[i]) + '\n')

                print('\nFilename: ' + getframeinfo(currentframe()).filename + ', Line = ' + str(getframeinfo(currentframe()).lineno))
                print('####################################################################')
                print('########################## ' + cls._name +' REWARD MATRIX ############################')
                print('####################################################################\n')

                print('Current offloading position: ' + cls._current_node.get_name() + '\n')
                for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS):
                    print(cls._offloading_sites[i].get_name() + ' updated R matrix: \n' + \
                        str(cls._R[i]) + '\n')


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
