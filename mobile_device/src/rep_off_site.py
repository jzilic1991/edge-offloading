from base_off_site import BaseOffloadingSite


class RepresentOffloadingSite (BaseOffloadingSite):

    def get_fail_trans_prob (cls):
        raise NotImplementedError

    
    def get_server_fail_prob (cls):
        raise NotImplementedError


    def get_net_fail_prob (cls):
        raise NotImplementedError


    def reset_test_data (cls):
        raise NotImplementedError


    def execute (cls, task):
        raise NotImplementedError


    def terminate_task (cls, task):
        raise NotImplementedError


    def detect_failure_event (cls, prob):
        raise NotImplementedError
