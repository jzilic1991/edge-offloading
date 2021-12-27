import sys
import psycopg2
import pandas as pd
from kivy.network.urlrequest import UrlRequest

from rep_off_site import RepresentOffloadingSite
from utilities import NodeType


class MobAppProfiler:

    def __init__ (self):
        self._mobile_app = None

        self.__get_mob_app_data ()


    def __get_mob_app_data (cls):
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
