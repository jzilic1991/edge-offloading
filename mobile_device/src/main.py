from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.network.urlrequest import UrlRequest
from kivy.lang import Builder

class MyWidget(BoxLayout):
   
    label_text = StringProperty()

    def __init__ (self, **kwargs):
        super (MyWidget, self).__init__(**kwargs)
        
        self.label_text = "Waiting for HTTP response..."
        self._search_url = "http://128.131.169.143:30927/get_avail_data?sysid=1&nodenum=0"
        self._request = UrlRequest (self._search_url, self.http_response)


    def http_response (self, *args):
        print (self._request.result)
        self.label_text = str(self._request.result[0])


class MyApp(App):

    def build(self):
        return MyWidget()


Builder.load_file("main_layout.kv")

if __name__ == '__main__':
    MyApp().run()
