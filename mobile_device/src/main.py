import psycopg2
import sys
import pandas as pd
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.network.urlrequest import UrlRequest
from kivy.lang import Builder

from mobile_device import MobileDevice


def get_md_data ():
    con = psycopg2.connect(database = "postgres", user = "postgres", password = "", host = "128.131.169.143", port = "32398")
    # print("Database opened successfully", file = sys.stdout)
    
    query = "SELECT * FROM offloading_sites WHERE id = \'Mobile Device\'"
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    con.close()

    col_names = []
    for elt in cur.description:
        col_names.append(elt[0])

    df = pd.DataFrame(data, columns = col_names)
    # print (df, file = sys.stdout)

    return df


class MyWidget(BoxLayout):
   
    _label_text = StringProperty()
    _mobile_device = None

    def __init__ (self, **kwargs):
        super (MyWidget, self).__init__(**kwargs)
        
        self._label_text = "DONE"
        #self._search_url = "http://128.131.169.143:30256/get_avail_data?sysid=1&nodenum=0"
        #self._request = UrlRequest (self._search_url, self.http_response)
        df = get_md_data ()
        self._mobile_device = MobileDevice (int(df['mips'][0]), int(df['memory'][0]), int(df['storage'][0]))
        
        self.__run_experiment (10, 1000)
        
        self._mobile_device.next_node_candidates ()
        self.__run_experiment (10, 1000)
        
        # self._mobile_device.next_node_candidates ()
        # self.__run_experiment (10, 1000)
        
        # self._mobile_device.next_node_candidates ()
        # self.__run_experiment (10, 1000)
        
        # self._mobile_device.next_node_candidates ()
        # self.__run_experiment (10, 1000)


    def __run_experiment (cls, samplings, executions):
        cls._mobile_device.deploy_mdp_svr_ode ()
        cls._mobile_device.run (samplings, executions)
        
        cls._mobile_device.deploy_efpo_ode ()
        cls._mobile_device.run (samplings, executions)


    # def http_response (self, *args):
    #     print (self._request.result)
    #     self.label_text = str(self._request.result[0])


class MyApp(App):

    def build(self):
        return MyWidget()


Builder.load_file("main_layout.kv")

if __name__ == '__main__':
    MyApp().run()
