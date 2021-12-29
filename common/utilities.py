import random
from abc import ABC


class Uptime:
    DAY_IN_MINUTES = 1440


class ExecutionErrorCode:
    EXE_NOK, EXE_OK = range(2)


class OffloadingSiteCode:
    MOBILE_DEVICE, EDGE_DATABASE_SERVER, EDGE_COMPUTATIONAL_INTENSIVE_SERVER, EDGE_REGULAR_SERVER, CLOUD_DATA_CENTER,\
            UNKNOWN = range(6)


class OffloadingActions:
    NUMBER_OF_OFFLOADING_ACTIONS = 5
    MOBILE_DEVICE, EDGE_DATABASE_SERVER, EDGE_COMPUTATIONAL_INTENSIVE_SERVER, EDGE_REGULAR_SERVER, CLOUD_DATA_CENTER = \
        range(NUMBER_OF_OFFLOADING_ACTIONS)


class FailureEventMode:
    POISSON_FAILURE, TEST_DATASET_FAILURE = range(2)


class OdeType:
    LOCAL, MOBILE_CLOUD, ENERGY_EFFICIENT, EFPO, MDP_SVR = ('LOCAL', 'MOBILE_CLOUD', 'ENERGY_EFFICIENT',\
        'EFPO', 'MDP_SVR')


class NodeType:
    MOBILE, EDGE_DATABASE, EDGE_COMPUTATIONAL, EDGE_REGULAR, CLOUD, UNKNOWN = ('Mobile Device', 'Edge Database Server',\
            'Edge Computational Intensive Server', 'Edge Regular Server', 'Cloud Data Center', 'Unknown')


class MobApps:
    ANTIVIRUS, GPS_NAVIGATOR, CHESS, FACERECOGNIZER, FACEBOOK = ('ANTIVIRUS', 'GPS NAVIGATOR', 'CHESS', 'FACERECOGNIZER', 'FACEBOOK')


class Tasks:
    DI, CI, MODERATE = ('DI', 'CI', 'MODERATE')


class Objective:
    
    def __init__ (self, execution, downlink, uplink, task_overall):
        self._execution = execution
        self._downlink = downlink
        self._uplink = uplink
        self._task_overall = task_overall

    def get_execution_energy (cls):
        return cls._execution


    def get_downlink_energy (cls):
        return cls._downlink


    def get_uplink_energy (cls):
        return cls._uplink


    def get_task_overall_energy (cls):
        return cls._task_overall


class ResponseTime (Objective):
    pass


class EnergyConsum (Objective):
    pass


class Util(object):

    @classmethod
    def determine_name_and_action (cls, name, offloading_site_code):
    
        if offloading_site_code == OffloadingSiteCode.EDGE_DATABASE_SERVER:
            return ('EDGE_DATABASE_SERVER_' + str(name), OffloadingActions.EDGE_DATABASE_SERVER)

        elif offloading_site_code == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
            return ('EDGE_COMPUTATIONAL_SERVER_' + str(name), OffloadingActions.EDGE_COMPUTATIONAL_INTENSIVE_SERVER)

        elif offloading_site_code == OffloadingSiteCode.EDGE_REGULAR_SERVER:
            return ('EDGE_REGULAR_SERVER_' + str(name), OffloadingActions.EDGE_REGULAR_SERVER)

        elif offloading_site_code == OffloadingSiteCode.CLOUD_DATA_CENTER:
            return ("CLOUD_DATA_CENTER_" + str(name), OffloadingActions.CLOUD_DATA_CENTER)

        else:
            raise ValueError ("Offloading site code is invalid! (" + str(offloading_site_code) + ")")


    @classmethod
    def determine_node_type (cls, node_type):

        node_type = str (node_type)

        if node_type == 'database':
            return NodeType.EDGE_DATABASE

        elif node_type == 'comp':
            return NodeType.EDGE_COMPUTATIONAL
        
        elif node_type == 'regular':
            return NodeType.EDGE_REGULAR

        elif node_type == 'cloud':
            return NodeType.CLOUD

        elif node_type == 'mobile':
            return NodeType.MOBILE

        else:
            return NodeType.UNKNOWN


    @classmethod
    def determine_off_site_code (cls, node_type):
        
        if isinstance (node_type, NodeType):
            return OffloadingSiteCode.UNKNOWN

        if node_type == NodeType.EDGE_DATABASE:
            return OffloadingSiteCode.EDGE_DATABASE_SERVER
        
        elif node_type == NodeType.EDGE_COMPUTATIONAL:
            return OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER

        elif node_type == NodeType.EDGE_REGULAR:
            return OffloadingSiteCode.EDGE_REGULAR_SERVER
        
        elif node_type == NodeType.CLOUD:
            return OffloadingSiteCode.CLOUD_DATA_CENTER

        elif node_type == NodeType.MOBILE:
            return OffloadingSiteCode.MOBILE_DEVICE

        else:
            return OffloadingSiteCode.UNKNOWN@classmethod


    @classmethod
    def generate_di_cpu_cycles(cls):
        return random.randint(100, 200)


    @classmethod
    def generate_ci_cpu_cycles(cls):
        return random.randint(550, 650)


    @classmethod
    def generate_random_cpu_cycles(cls):
        return random.randint(100, 200)


    @classmethod
    def generate_di_input_data(cls):
        return random.randint(4 * 25, 4 * 30)


    @classmethod
    def generate_random_input_data(cls):
        return random.randint(4, 8)


    @classmethod
    def generate_ci_input_data(cls):
        return random.randint(4, 8)


    @classmethod
    def generate_di_output_data(cls):
        return random.randint(4 * 15, 4 * 20)


    @classmethod
    def generate_random_output_data(cls):
        return random.randint(4, 8)


    @classmethod
    def generate_ci_output_data(cls):
        return random.randint(4, 8)
