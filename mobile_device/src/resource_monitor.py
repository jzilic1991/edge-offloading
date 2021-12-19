import sys
import psycopg2
import pandas as pd


class ResourceMonitor:

    def get_offloading_sites (self, query):
        con = psycopg2.connect(database = "postgres", user = "postgres", password = "", host = "128.131.169.143", port = "32398")
        print("Database opened successfully", file = sys.stdout)
    
        cur = con.cursor()
        cur.execute(query)
        data = cur.fetchall()

        col_names = []
        for elt in cur.description:
            col_names.append(elt[0])

        df = pd.DataFrame(data, columns = col_names)
        print (df, file = sys.stdout)
        con.close()

        return df
