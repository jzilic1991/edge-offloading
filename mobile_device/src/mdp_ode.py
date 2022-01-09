import random
import math 
import mdptoolbox
import time 
import numpy as np

from ode import OffloadingDecisionEngine
from utilities import OffloadingSiteCode, ExecutionErrorCode, OffloadingActions, ResponseTime, EnergyConsum
from task import Task
from logger import Logger
from fail_detector import FailureDetector


class MdpOde(OffloadingDecisionEngine):

    def initialize_params(cls):
        cls.__init_MDP_settings()


    def offload(cls, tasks):
        cls.__evaluate_params (tasks)

        cls._previous_node = cls._current_node
        task_completion_time_array = tuple()
        task_energy_consumption_array = tuple()
        task_overall_reward_array = tuple()
        validity_vector = [True for i in range(len(cls._offloading_sites))]
        non_offloadable_flag = False

        # determines are there any failure events on offloading sites
        cls._offloading_sites = FailureDetector.eval_fail_event (cls._offloading_sites) 
    
        for task in tasks:
            if task.is_offloadable() and non_offloadable_flag == False:
                non_offloadable_flag = True
                #cls._OffloadingDecisionEngine__increment_discrete_epoch_counters()

            task_completion_time = 0
            task_energy_consumption = 0
            task_overall_reward = 0
            task_failure_time_cost = 0
            task_failure_energy_cost = 0
            task_failures = 0
            candidate_node = None

            while True:
                # if task is not offloadable, then mobile device is considered as offloading site for task execution
                candidate_node, validity_vector = cls.__offloading_decision(task, validity_vector)
    
                # random offloading site checks validity of such task deployment regards to it's own resource capacity
                if not candidate_node.check_validity_of_deployment(task):
                    raise ValueError(candidate_node.get_name() + " does not have validity for task deployment!")

                Logger.w ('\n\n\n\n\n' + cls._previous_node.get_name() + " -> " + candidate_node.get_name())
                Logger.w ('Offloading task ' + task.get_name() + ' (off = ' + str(task.is_offloadable()) + ')\n')
                (task_rsp_time, task_energy_consum) = cls.__compute_objectives (task, cls._previous_node, candidate_node)
                task_completion_time_tmp = task_rsp_time.get_task_overall()
                task_energy_consumption_tmp = task_energy_consum.get_task_overall()

                # if task deployment on offloading site is valid, then task is going to be executed
                if not candidate_node.execute(task):
                    Logger.w("FAILURE occurs on node " + candidate_node.get_name())
                    validity_vector = cls.recovery_action(validity_vector, candidate_node.get_offloading_action_index())
                    cls._statistics.add_offload_fail(candidate_node.get_name())
                    task_failures += 1

                    (cost_rsp_time, cost_energy_consum, cost_reward) = \
                        cls._OffloadingDecisionEngine__compute_failure_cost(candidate_node, cls._previous_node)

                    task_completion_time_tmp = cost_rsp_time.get_task_overall()
                    task_energy_consumption_tmp = cost_energy_consum.get_task_overall()
                    task_overall_reward_tmp = cost_reward

                    task_completion_time = task_completion_time + task_completion_time_tmp
                    task_failure_time_cost += task_completion_time_tmp

                    task_energy_consumption = task_energy_consumption + task_energy_consumption_tmp
                    task_failure_energy_cost += task_energy_consumption_tmp

                    task_overall_reward = task_overall_reward - task_overall_reward_tmp

                    if any(validity_vector):
                        continue
                    
                    else:
                        raise ValueError("None of the offloading sites can execute task " + \
                            task.get_name() + " due to resource limitations or offloading failures!")

                task_completion_time = round(task_completion_time + task_completion_time_tmp, 3)
                task_completion_time_array += (task_completion_time,)
                task_energy_consumption = round(task_energy_consumption + task_energy_consumption_tmp, 3)
                task_energy_consumption_array += (task_energy_consumption,)
                
                Logger.w ('Task ' + task.get_name() + ' is offloaded on ' + candidate_node.get_name())
                Logger.w("Complete task completion time: " + str(task_completion_time) + " s")
                Logger.w("Complete task energy: " + str(task_energy_consumption) + " J")

                task_time_completion_reward = cls._OffloadingDecisionEngine__compute_task_time_completion_reward\
                        (task_completion_time)
                task_energy_consumption_reward = cls._OffloadingDecisionEngine__compute_task_energy_consumption_reward\
                        (task_energy_consumption)
                task_overall_reward_tmp = round(cls._OffloadingDecisionEngine__compute_overall_task_reward\
                        (task_time_completion_reward, task_energy_consumption_reward), 3)
                Logger.w("Reward: " + str(task_overall_reward_tmp) + '\n')
    
                task_overall_reward = task_overall_reward + task_overall_reward_tmp
                task_overall_reward_array += (task_overall_reward),
                Logger.w("Complete task reward: " + str(task_overall_reward) + "\n")

                break

            cls._current_node = candidate_node
            cls._statistics.add_offload(cls._current_node.get_name())

            # task.save_offloading_site(cls._current_node.get_name())
            # task.save_offloading_policy(cls._policy)

            cls._current_node.flush_executed_task(task)

        max_task_completion_time = 0
        for task_completion_time in task_completion_time_array:
            if max_task_completion_time < task_completion_time:
                max_task_completion_time = task_completion_time

        acc_task_energy_consumption = 0
        for task_energy_consumption in task_energy_consumption_array:
            acc_task_energy_consumption += task_energy_consumption

        acc_task_overall_rewards = 0
        for task_overall_reward in task_overall_reward_array:
            acc_task_overall_rewards += task_overall_reward

        return (max_task_completion_time, acc_task_energy_consumption, acc_task_overall_rewards, task_failure_time_cost, \
                task_failure_energy_cost, task_failures)



    def __init_MDP_settings(cls):
        cls._P = np.array([[[0.0 for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS)] \
                for i in range(len(cls._offloading_sites))] for i in range(len(cls._offloading_sites))])
        cls._R = np.array([[[0.0 for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS)] \
                for i in range(len(cls._offloading_sites))] for i in range(len(cls._offloading_sites))])
        cls._response_time_matrix = np.array([[[0.0 for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS)] \
                for i in range(len(cls._offloading_sites))] for i in range(len(cls._offloading_sites))])

        # print ("Offloading sites: " + str(cls._offloading_sites))

        if (cls._P.size / cls._P[0].size) != OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS:
            raise ValueError("Size of P matrix is not correct! It should contain " + \
                str(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS) + " action submatrices but it has "+ \
                str(cls._P.size / cls._P[0].size) + ".")

        for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS):
            if math.ceil(cls._P[i].size / cls._P[i][0].size) != len(cls._offloading_sites):
                raise ValueError("Number of rows of each action submatrix should be equal to number of offloading sites! Offloading sites = " + \
                str(len(cls._offloading_sites)) + ", matrix rows = " + str(math.ceil(cls._P[i].size / cls._P[i][0].size)) + " for " + \
                str(i + 1) + ".action submatrix. P[" + str(i) + "] = " + str(cls._P[i]))

            for j in range(len(cls._offloading_sites)):
                if cls._P[i][j].size != len(cls._offloading_sites):
                    raise ValueError("Size of " + str(i + 1) + ".action submatrix row should be equal to number of offloading sites " +\
                            str(len(cls._offloading_sites)) + " but it is " + str(cls._P[i][j].size))

        cls._discount_factor = 0.96
        cls._policy = ()
        
        # print ('Init P matrix = ' + str(cls._P))
        # print ('Init R matrix = ' + str(cls._R))


    def __offloading_decision(cls, task, validity_vector):
        while True:
            if not task.is_offloadable():
                for i in range(len(validity_vector)):
                    if cls._offloading_sites[i].get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
                        validity_vector[i] = False
                
                return (cls._mobile_device, validity_vector)

            offloading_site_index = cls._current_node.get_offloading_action_index()
    
            cls._policy = cls.__MDP_run(task, validity_vector)
            Logger.w("Current node: " + cls._current_node.get_name())
            Logger.w("Current offloading policy: " + str(cls._policy))

            if cls._policy[offloading_site_index] == OffloadingActions.MOBILE_DEVICE:
                return (cls._offloading_sites[cls._mobile_device.get_offloading_action_index()], validity_vector)
    
            trans_prob = ()
            action_index = cls._policy[offloading_site_index]
            source_node_index = cls._current_node.get_offloading_action_index()
            P_matrix_columns = len(cls._P[action_index][source_node_index])
            # print("P matrix columns [action = " + str(action_index) + "][source_node = " + \
            #    str(source_node_index) + "] = " + str(cls._P[action_index][source_node_index]))

            for i in range(P_matrix_columns):
                if cls._P[action_index][source_node_index][i] != 0.0 and i != cls._mobile_device.get_offloading_action_index():
                    trans_prob = trans_prob + (1.0,)
                    
                else:
                    trans_prob = trans_prob + (0.0,)
    

            offloading_site_index = np.random.choice(P_matrix_columns, 1, p = trans_prob)[0]

            if cls._offloading_sites[offloading_site_index].get_offloading_site_code() == \
                OffloadingSiteCode.MOBILE_DEVICE:
                validity_vector[action_index] = False

                if any(validity_vector):
                    continue
                    
                else:
                    offloading_site_index = cls._mobile_device.get_offloading_action_index()
                    break

            break

        return (cls._offloading_sites[offloading_site_index], validity_vector)
    

    def __compute_objectives (cls, task, previous_node, candidate_node):
        task_rsp_time = cls._OffloadingDecisionEngine__compute_complete_task_time_completion\
            (task, candidate_node, previous_node)
        Logger.w("Uplink time: " + str(task_rsp_time.get_uplink()) + "s")
        Logger.w("Execution time: " + str(task_rsp_time.get_execution()) + "s")
        Logger.w("Downlink time: " + str(task_rsp_time.get_downlink()) + "s")
        Logger.w("Task completion time: " + str(task_rsp_time.get_task_overall()) + "s\n")

        task_energy_consum = cls._OffloadingDecisionEngine__compute_complete_energy_consumption\
            (task_rsp_time, candidate_node, previous_node)
        Logger.w("Uplink energy: " + str(task_energy_consum.get_uplink()) + "J")
        Logger.w("Execution/Idle energy: " + str(task_energy_consum.get_execution()) + "J")
        Logger.w("Downlink energy: " + str(task_energy_consum.get_downlink()) + "J")
        Logger.w("Task energy: " + str(task_energy_consum.get_task_overall()) + "J")

        return (task_rsp_time, task_energy_consum)


    def __MDP_run(cls, task, validity_vector):
        cls.update_P_matrix()
        cls.update_R_matrix(task, validity_vector)

        # Logger.w("P = " + str(cls._P))
        # Logger.w("R = " + str(cls._R))

        PIA = mdptoolbox.mdp.PolicyIteration(cls._P, cls._R, cls._discount_factor)
        PIA.verbose = False
        PIA.run()
        return PIA.policy


    def __evaluate_params (cls, tasks):
        if not tasks:
            raise ValueError("Tasks should not be empty in ODE class!")

        for task in tasks:
            if not isinstance(task, Task):
                raise ValueError("Tasks should be Task object instance in ODE class!")
