from base_off_site import BaseOffloadingSite


class RemoteOffloadingSite (BaseOffloadingSite):


    @abstractmethod
    def get_fail_trans_prob (cls):
        pass

    
    @abstractmethod
    def get_server_fail_prob (cls):
        pass


    @abstractmethod
    def get_net_fail_prob (cls):
        pass


    @abstractmethod
    def reset_test_data (cls):
        pass


    @abstractmethod
    def execute (cls, task):
        pass


    @abstractmethod
    def terminate_task (cls, task):
        pass


    @abstractmethod
    def detect_failure_event (cls, prob):
        pass
