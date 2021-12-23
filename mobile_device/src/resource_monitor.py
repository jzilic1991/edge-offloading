import sys
import psycopg2
import pandas as pd

from rep_off_site import RepresentOffloadingSite
from utilities import NodeType


class ResourceMonitor:

    def __init__ (self):
        self._edge_reg_server = None
        self._edge_dat_server = None
        self._edge_comp_server = None
        self._cloud_dc = None

        self.__get_off_sites ()


    def __get_off_sites (cls):
        con = psycopg2.connect(database = "postgres", user = "postgres", password = "", host = "128.131.169.143", port = "32398")
        print("Database opened successfully", file = sys.stdout)
    
        query = "SELECT * FROM offloading_sites WHERE id != \'Mobile Device\'"
        cur = con.cursor()
        cur.execute(query)
        data = cur.fetchall()

        col_names = []
        for elt in cur.description:
            col_names.append(elt[0])

        df = pd.DataFrame(data, columns = col_names)
        print (df, file = sys.stdout)
        con.close()

        for i, data in df.iterrows():
            if str(data['id']) == 'Edge Database Server':
                cls._edge_dat_server = RepresentOffloadingSite (int(data['mips']), int(data['memory']), \
                        int(data['storage']), NodeType.EDGE_DATABASE, str(data['name']))

            elif str(data['id']) == 'Edge Computational Intensive Server':
                cls._edge_comp_server = RepresentOffloadingSite (int(data['mips']), int(data['memory']), \
                        int(data['storage']), NodeType.EDGE_COMPUTATIONAL, str(data['name']))
            
            elif str(data['id']) == 'Edge Regular Server':
                cls._edge_reg_server = RepresentOffloadingSite (int(data['mips']), int(data['memory']), \
                        int(data['storage']), NodeType.EDGE_REGULAR, str(data['name']))
            
            elif str(data['id']) == 'Cloud Data Center':
                cls._cloud_dc = RepresentOffloadingSite (int(data['mips']), int(data['memory']), \
                        int(data['storage']), NodeType.CLOUD, str(data['name']))
