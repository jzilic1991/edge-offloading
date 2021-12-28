import sys
import psycopg2
import pandas as pd
import numpy as np

from mobile_app import MobileApplication
from task import Task
from utilities import Util, Tasks


class MobileAppProfiler:

    def __init__ (self):
        self._mobile_app = None

        mob_apps = self.__get_query_results ("SELECT * FROM mobile_applications")
        app_tasks = self.__get_query_results ("SELECT * FROM application_tasks")

        self._mobile_applications = self.__instantiate_mobile_apps (mob_apps, app_tasks)

    
    def deploy_random_mobile_app (cls):
        choice = np.random.choice(len(cls._mobile_applications), 1, \
            p = [app.get_prob() for app in cls._mobile_applications])[0]

        return cls._mobile_applications[choice]


    def __get_query_results (cls, query):
        con = psycopg2.connect(database = "postgres", user = "postgres", password = "", host = "128.131.169.143", port = "32398")
        print("Database opened successfully", file = sys.stdout)
    
        cur = con.cursor()
        cur.execute(query)
        data = cur.fetchall()
        con.close()

        col_names = list ()
        for elt in cur.description:
            col_names.append(elt[0])
        
        df = pd.DataFrame (data, columns = col_names)
        print (df, file = sys.stdout)

        return df
    

    def __instantiate_mobile_apps (cls, mob_apps, app_tasks):
        tasks = list ()
        applications = list ()
        
        for _, app in mob_apps.iterrows():
            dag_structure = dict ()
            
            for _, task_ in app_tasks.iterrows():
                if app['id'] != task_['application_id']:
                    continue

                cpu_cycles = 0
                input_data = 0
                output_data = 0
                    
                if task_['component'] == Tasks.MODERATE:
                    cpu_cycles = Util.generate_random_cpu_cycles ()
                    input_data = Util.generate_random_input_data ()
                    output_data = Util.generate_random_output_data ()

                elif task_['component'] == Tasks.DI:
                    cpu_cycles = Util.generate_di_cpu_cycles ()
                    input_data = Util.generate_di_input_data ()
                    output_data = Util.generate_di_output_data ()

                elif task_['component'] == Tasks.CI:
                    cpu_cycles = Util.generate_ci_cpu_cycles ()
                    input_data = Util.generate_ci_input_data ()
                    output_data = Util.generate_ci_output_data ()
                    
                task = Task (task_['name'], cpu_cycles, task_['memory'], input_data, \
                    output_data, task_['offloadability'])
                dag_structure.update ({task: task_['next_tasks']})
        
            applications.append (MobileApplication (app['id'], dag_structure, app['prob']))

        return applications
