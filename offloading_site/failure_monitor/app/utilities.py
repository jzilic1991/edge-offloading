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
    MOBILE_DEVICE, EDGE_DATABASE_SERVER, EDGE_COMPUTATIONAL_INTENSIVE_SERVER, EDGE_REGULAR_SERVER, CLOUD_DATA_CENTER = range(5)


class OffloadingActions:
    NUMBER_OF_OFFLOADING_ACTIONS = 5
    MOBILE_DEVICE, EDGE_DATABASE_SERVER, EDGE_COMPUTATIONAL_INTENSIVE_SERVER, EDGE_REGULAR_SERVER, CLOUD_DATA_CENTER = \
        range(NUMBER_OF_OFFLOADING_ACTIONS)


class FailureEventMode:
    POISSON_FAILURE, TEST_DATASET_FAILURE = range(2)


class OdeType:
    LOCAL, MOBILE_CLOUD, ENERGY_EFFICIENT, EFPO, MDP_SVR = ('LOCAL', 'MOBILE_CLOUD', 'ENERGY_EFFICIENT',\
        'EFPO', 'MDP_SVR')


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
