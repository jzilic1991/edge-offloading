class NodeCategory:
    ER_DATA, EC_DATA, ED_DATA, CD_DATA, NET_DATA = ("EDGE_REG_DATA", "EDGE_COMP_DATA", "EDGE_DATA_DATA", \
        "CLOUD_DATA", "NETWORK_DATA")


class TrainingDataSize:
    SIZE_526 = 526


class DatasetType:
    LANL_DATASET, PNNL_DATASET, LDNS_DATASET = ("LANL", "PNNL", "LDNS")


class PredictionMode:
    TEST_PREDICTION_MODE, TRAINING_PREDICTION_MODE = ("test", "training")


class SlidingWindowSize:
    SIZE_1, SIZE_2, SIZE_5, SIZE_10, SIZE_15, SIZE_20, SIZE_30, SIZE_40, SIZE_50, SIZE_70, SIZE_100 = (1, 2, 5, 10, 15, 20, 30, 40, 50, 70, 100)


class ExecutionMode:
    NORMAL_MODE, EXHAUSTIVE_MODE = (1, 2)


class DataType:
    TIME_BETWEEN_FAILURE, FAILURE_RATE, AVAILABILITY = ('TBF', 'FR', 'AVAIL')


class Uptime:
    DAY_IN_MINUTES = 1440


class WorkingCondition:
    SLIDING_WINDOW, TRAINING_TEST_SEPARATION = ('SLIDING_WINDOW', 'TRAINING_TEST_SEPARATION')


class PredictionSample:
    MTBF, SVR = ('MTBF', 'SVR')


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
            return OffloadingSiteCode.UNKNOWN
