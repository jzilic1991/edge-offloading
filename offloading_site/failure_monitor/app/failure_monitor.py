import matplotlib.pyplot as plt
import pandas as pd
import sys

from utilities import Util, OffloadingSiteCode, NodeType
from dataset import Dataset

CONVERSION_SYSTEM_ID_DICT = {2: (20, OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER),
                             3: (9, OffloadingSiteCode.EDGE_REGULAR_SERVER),
                             4: (10, OffloadingSiteCode.EDGE_REGULAR_SERVER),
                             5: (11, OffloadingSiteCode.EDGE_REGULAR_SERVER),
                             6: (12, OffloadingSiteCode.EDGE_DATABASE_SERVER),
                             7: (1, OffloadingSiteCode.EDGE_DATABASE_SERVER),
                             8: (4, OffloadingSiteCode.EDGE_REGULAR_SERVER),
                             9: (13, OffloadingSiteCode.EDGE_REGULAR_SERVER),
                             10: (14, OffloadingSiteCode.EDGE_REGULAR_SERVER),
                             11: (15, OffloadingSiteCode.EDGE_REGULAR_SERVER),
                             12: (18, OffloadingSiteCode.EDGE_REGULAR_SERVER),
                             13: (16, OffloadingSiteCode.EDGE_REGULAR_SERVER),
                             14: (17, OffloadingSiteCode.EDGE_REGULAR_SERVER),
                             15: (22, OffloadingSiteCode.CLOUD_DATA_CENTER),
                             16: (19, OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER),
                             18: (7, OffloadingSiteCode.EDGE_DATABASE_SERVER),
                             19: (8, OffloadingSiteCode.EDGE_DATABASE_SERVER),
                             20: (5, OffloadingSiteCode.EDGE_DATABASE_SERVER),
                             21: (6, OffloadingSiteCode.EDGE_DATABASE_SERVER),
                             22: (3, OffloadingSiteCode.EDGE_REGULAR_SERVER),
                             23: (21, OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER),
                             24: (2, OffloadingSiteCode.EDGE_REGULAR_SERVER)}

EMPTY_SYSTEM_ID = 17


class FailureMonitor:

        def __init__(self, file, node_type):
            self._dataset = pd.read_csv(file, encoding = 'utf-8', index_col = False)
            self._data_stats = self.__determine_dataset (node_type)
            
            self.__parse_dataset()
        

        def get_dataset (cls):
            return cls._data_stats


        def get_avail_data (cls, sysid, nodenum):
            data = cls._data_stats.get_node_avail_data (sysid, nodenum)
            # cls.__plot_avail_dist (data)
            return data # (avail_data, mtbf)

        
        def __determine_dataset (cls, node_type):
            node_type = Util.determine_node_type (node_type)

            if node_type == NodeType.EDGE_DATABASE:
                return Dataset (OffloadingSiteCode.EDGE_DATABASE_SERVER)
            
            elif node_type == NodeType.EDGE_COMPUTATIONAL:
                return Dataset (OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER)

            elif node_type == NodeType.EDGE_REGULAR:
                return Dataset (OffloadingSiteCode.EDGE_REGULAR_SERVER)

            elif node_type == NodeType.CLOUD:
                return Dataset (OffloadingSiteCode.CLOUD_DATA_CENTER)

            else:
                raise ValueError ('Wrong node type for Dataset class! Value: ' + str(node_type))


        def __parse_dataset(cls):
            for index, row in cls._dataset.iterrows():
                system_id = int(row['System'])

                if system_id == EMPTY_SYSTEM_ID:
                    continue
                
                (row['System'], offloading_site_code) = cls.__get_system_data (system_id)

                if offloading_site_code == cls._data_stats.get_offloading_site_code():
                    cls._data_stats.add_item (row)

            print ('Failure monitor is started!', file = sys.stdout)


        def __get_system_data (cls, system_id):
            return (CONVERSION_SYSTEM_ID_DICT[system_id][0], CONVERSION_SYSTEM_ID_DICT[system_id][1])


        def __plot_avail_dist (cls, data):
            plt.plot(tuple(i for i in range(len(data))), data)
            plt.suptitle('#data_points = ' + str(len(data) + 1))
            plt.title('Availability distribution')
            plt.xlabel('Failure index')
            plt.ylabel('Availability (per day)')
            plt.show()
