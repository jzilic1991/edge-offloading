import pandas as pd
import sys

from utilities import OffloadingSiteCode
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

        def __init__(self, file):
            self._dataset = pd.read_csv(file, encoding = 'utf-8', index_col = False)
            self._ec_data_stats = Dataset(OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER)
            self._ed_data_stats = Dataset(OffloadingSiteCode.EDGE_DATABASE_SERVER)
            self._er_data_stats = Dataset(OffloadingSiteCode.EDGE_REGULAR_SERVER)
            self._cd_data_stats = Dataset(OffloadingSiteCode.CLOUD_DATA_CENTER)
            
            self.__parse_dataset()
        

        def get_datasets (cls):
            return (cls._ec_data_stats, cls._ed_data_stats, cls._er_data_stats, cls._cd_data_stats)


        def get_ec_data_stats(cls):
            return cls._ec_data_stats


        def get_ed_data_stats(cls):
            return cls._ed_data_stats


        def get_er_data_stats(cls):
            return cls._er_data_stats


        def get_cd_data_stats(cls):
            return cls._cd_data_stats
        

        def get_avail_data (cls, sysid, nodenum):
            return cls._ed_data_stats.get_node_avail_data(sysid, nodenum)


        def __parse_dataset(cls):
            for index, row in cls._dataset.iterrows():
                system_id = int(row['System'])

                if system_id == EMPTY_SYSTEM_ID:
                    continue

                (row['System'], offloading_site_code) = cls.__get_system_data(system_id)

                if offloading_site_code == cls._ec_data_stats.get_offloading_site_code():
                    cls._ec_data_stats.add_item(row)

                elif offloading_site_code == cls._ed_data_stats.get_offloading_site_code():
                    cls._ed_data_stats.add_item(row)

                elif offloading_site_code == cls._er_data_stats.get_offloading_site_code():
                    cls._er_data_stats.add_item(row)

                elif offloading_site_code == cls._cd_data_stats.get_offloading_site_code():
                    cls._cd_data_stats.add_item(row)

                else:
                    exit("Data row must correspond to one of data categories!\n Data: " + str(row))

            print ('Failure monitor is started!', file = sys.stdout)


        def __get_system_data (cls, system_id):
            return (CONVERSION_SYSTEM_ID_DICT[system_id][0], CONVERSION_SYSTEM_ID_DICT[system_id][1])
