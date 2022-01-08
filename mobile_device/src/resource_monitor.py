import sys
import psycopg2
import pandas as pd
from kivy.network.urlrequest import UrlRequest

from rep_off_site import RepresentOffloadingSite
from utilities import NodeType, OffloadingActions, ReqStateMachine


class ResourceMonitor:

    def __init__ (self, mobile_device):
        self._mobile_device = mobile_device
        self._edge_reg_server = None
        self._edge_dat_server = None
        self._edge_comp_server = None
        self._cloud_dc = None
        self._net_conns = self.__get_net_conn_data ()

        self.__get_off_site_data ()


    def get_edge_reg_server (cls):
        return cls._edge_reg_server


    def get_edge_dat_server (cls):
        return cls._edge_dat_server


    def get_edge_comp_server (cls):
        return cls._edge_comp_server


    def get_cloud_dc (cls):
        return cls._cloud_dc
    

    def get_edge_servers (cls):
        return [cls._edge_reg_server, cls._edge_dat_server, cls._edge_comp_server]


    def next_node_candidates (cls):
        cls._edge_reg_server.next_node_candidate ()
        cls._edge_dat_server.next_node_candidate ()
        cls._edge_comp_server.next_node_candidate ()
        cls._cloud_dc.next_node_candidate ()
        cls.__are_requests_done ()


    def reset_test_data (cls):
        cls._edge_reg_server.reset_test_data ()
        cls._edge_dat_server.reset_test_data ()
        cls._edge_comp_server.reset_test_data ()
        cls._cloud_dc.reset_test_data ()
        cls.__are_requests_done ()


    def get_network_bandwidth (cls, first_site, second_site):
        for _, net_conn in cls._net_conns.iterrows():
            if (first_site.get_node_type() == net_conn['first_site_id'] or \
                    first_site.get_node_type() == net_conn['second_site_id']) and\
                    (second_site.get_node_type() == net_conn['first_site_id'] or \
                    second_site.get_node_type() == net_conn['second_site_id']):
                return net_conn['bandwidth']

        return 0.0


    def get_off_sites (cls):
        off_sites = [None for i in range (OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS)]

        off_sites[cls._mobile_device.get_offloading_action_index ()] = cls._mobile_device
        off_sites[cls._edge_reg_server.get_offloading_action_index ()] = cls._edge_reg_server
        off_sites[cls._edge_dat_server.get_offloading_action_index ()] = cls._edge_dat_server
        off_sites[cls._edge_comp_server.get_offloading_action_index ()] = cls._edge_comp_server
        off_sites[cls._cloud_dc.get_offloading_action_index ()] = cls._cloud_dc
        
        return off_sites


    def get_edge_servers (cls):
        return (cls._edge_dat_server, cls._edge_reg_server, cls._edge_comp_server)


    def get_cloud_dc (cls):
        return cls._cloud_dc


    def __are_requests_done (cls):
        off_sites = [cls._edge_reg_server, cls._edge_dat_server, cls._edge_comp_server, cls._cloud_dc]

        while True:
            all_positive = True
            for site in off_sites:
                if site.get_req_state() != ReqStateMachine.IDLE:
                    all_positive = False
                    break

            if all_positive:
                break



    def __get_net_conn_data (cls):
        con = psycopg2.connect(database = "postgres", user = "postgres", password = "", host = "128.131.169.143", port = "32398")
        # print("Database opened successfully", file = sys.stdout)
    
        query = "SELECT * FROM network_connections"
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


    def __get_off_site_data (cls):
        con = psycopg2.connect(database = "postgres", user = "postgres", password = "", host = "128.131.169.143", port = "32398")
        # print("Database opened successfully", file = sys.stdout)
    
        query = "SELECT * FROM offloading_sites WHERE id != \'Mobile Device\'"
        cur = con.cursor()
        cur.execute(query)
        data = cur.fetchall()
        con.close()

        col_names = []
        for elt in cur.description:
            col_names.append(elt[0])

        df = pd.DataFrame(data, columns = col_names)
        # print (df, file = sys.stdout)

        for i, data in df.iterrows():
            if str(data['id']) == 'Edge Database Server':
                cls._edge_dat_server = RepresentOffloadingSite (int(data['mips']), int(data['memory']), \
                        int(data['storage']), NodeType.EDGE_DATABASE, str(data['url_svc']), str(data['name']))

            elif str(data['id']) == 'Edge Computational Intensive Server':
                cls._edge_comp_server = RepresentOffloadingSite (int(data['mips']), int(data['memory']), \
                        int(data['storage']), NodeType.EDGE_COMPUTATIONAL, str(data['url_svc']), str(data['name']))
            
            elif str(data['id']) == 'Edge Regular Server':
                cls._edge_reg_server = RepresentOffloadingSite (int(data['mips']), int(data['memory']), \
                        int(data['storage']), NodeType.EDGE_REGULAR, str(data['url_svc']), str(data['name']))
            
            elif str(data['id']) == 'Cloud Data Center':
                cls._cloud_dc = RepresentOffloadingSite (int(data['mips']), int(data['memory']), \
                        int(data['storage']), NodeType.CLOUD, str(data['url_svc']), str(data['name']))
