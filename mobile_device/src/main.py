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
    print("Database opened successfully", file = sys.stdout)
    
    query = "SELECT * FROM offloading_sites WHERE id = \'Mobile Device\'"
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


class MyWidget(BoxLayout):
   
    _label_text = StringProperty()
    _mobile_device = None

    def __init__ (self, **kwargs):
        super (MyWidget, self).__init__(**kwargs)
        
        self._label_text = "Waiting for HTTP response..."
        #self._search_url = "http://128.131.169.143:30256/get_avail_data?sysid=1&nodenum=0"
        #self._request = UrlRequest (self._search_url, self.http_response)
        df = get_md_data ()
        self._mobile_device = MobileDevice (int(df['mips'][0]), int(df['memory'][0]), int(df['storage'][0]))
        self._mobile_device.print_system_config ()
        self._mobile_device.run (1, 1)
        
        #self._res_monitor.get_offloading_sites ("SELECT * FROM offloading_sites WHERE id != \'Mobile Device\'")


    def http_response (self, *args):
        print (self._request.result)
        self.label_text = str(self._request.result[0])


class MyApp(App):

    def build(self):
        return MyWidget()


Builder.load_file("main_layout.kv")

if __name__ == '__main__':
    MyApp().run()
