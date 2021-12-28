import sys

from task import Task
from utilities import ExecutionErrorCode


class MobileApplication:

    def __init__(self, name, delay_dict, prob):
        self.__evaluate_params(delay_dict)

        self._name = name
        self._delay_dict = delay_dict
        self._prob = prob
        self._running = False

        self.__init_task_dependencies()
        self.print_entire_config ()
        
        #for task in self._delay_dict:
        #    task.print_dependencies()


    def run(cls):
        if not cls._running:
            cls._running = True


    def get_prob (cls):
        return cls._prob


    def get_name(cls):
        return cls._name

    
    def get_ready_tasks(cls):
        ready_tasks = ()

        if not cls._running:
            return False

        for task in cls._delay_dict:
            if not task.get_in_edges() and not task.is_executed():
                ready_tasks = ready_tasks + (task,)

            if not ready_tasks:
                for task in cls._delay_dict:
                    if not task.is_executed():
                        return False

            cls.print_task_exe_status()
            cls.__init_task_dependencies()
            cls._running = False

        return ready_tasks


    def print_task_dependencies(cls):
        print("******** TASK DEPENDENCIES ********", file = sys.stdout)
        
        for key, values in cls._delay_dict.items():
            for value in values:
                print(key.get_name() + " ----------> " + value, file = sys.stdout)
                print('\n\n', file = sys.stdout)


    def print_task_config(cls):
        for task in cls._delay_dict:
            task.print_system()


    def print_task_exe_status(cls):
        for task in cls._delay_dict:
            if task.is_executed():
                offloadability = task.is_offloadable()
                print_text = task.get_name() + "(" + str(offloadability) + ")" + " is EXECUTED on " + task.get_offloading_site() 
    
                if offloadability:
                    print_text = print_text + " with offloading policy " + str(task.get_offloading_policy())

    
    def print_entire_config(cls):
        print("######## " + cls._name + " APPLICATION CONFIGURATION ##########", file = sys.stdout)
        print('\n', file = sys.stdout)

        cls.print_task_dependencies()
        cls.print_task_config()
        cls.print_task_exe_status()


    def __init_task_dependencies(cls):
        for key, values in cls._delay_dict.items():
            for value in values:
                key.add_out_edge (value)
                
                for key_ in cls._delay_dict:
                    if key_.get_name() == value:
                        key_.add_in_edge (key.get_name())
                        break

            key.reset_exec_flag()

    
    def __evaluate_params(cls, delay_dict):
        if not delay_dict:
            raise ValueError("Delay dictionary should not be empty!")
        
        if type(delay_dict) is not dict:
            raise TypeError("Tasks should be a dictionary data type!")

        for key, values in delay_dict.items():
            if type(key) is not Task:
                raise TypeError("Key in delay dictionary should be Task class instance!")
            
            if type(values) is not list:
                raise TypeError("Values should be a list!")
