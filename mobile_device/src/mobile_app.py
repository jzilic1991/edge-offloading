from task import Task
from utilities import ExecutionErrorCode


class MobileApplication:

    def __init__(self, name, delay_dict):
        self.__evaluate_params(delay_dict)

        self._name = name
        self._delay_dict = delay_dict
        self._running = False

        self.__init_task_dependencies()

        for task in self._delay_dict:
            task.print_dependencies()


    def run(cls):
        if not cls._running:
            cls._running = True


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


    def print_entire_config(cls):
        print("######################################## " + cls._name + " APPLICATION CONFIGURATION ########################################")
        print('\n')

        cls.print_task_dependencies()
        cls.print_task_config()
        cls.print_task_exe_status()


    def print_task_dependencies(cls):
        print("********************** TASK DEPENDENCIES **********************")
        for key, values in cls._delay_dict.items():
            for value in values:
                print(key.get_name() + " -----(" + str(value[1]) + " s)-----> " + value[0].get_name())
                print('\n\n')


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


    def __init_task_dependencies(cls):
        for key, values in cls._delay_dict.items():
            for value in values:
                key.add_out_edge(value[0])
                value[0].add_in_edge(key)

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
            
            for value in values:
                if len(value) != 2:
                    raise ValueError("Tuple in delay dictionary must have length equal to 2 (task <Task>, delay <int>)!")
                
                if not isinstance(value[0], Task):
                    raise TypeError("First value of tuple in delay dictionary should be class Task instance (task <Task>, delay <int>)!")
                
                if type(value[1]) is not int or value[1] <= 0:
                    raise ValueError("Second value of tuple in delay dictionary should be positive integer (task <Task>, delay <int>)!")
