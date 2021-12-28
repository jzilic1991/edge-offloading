from utilities import ExecutionErrorCode

class Task:
    
    def __init__(self, name, millions_of_instructions, memory, data_in, data_out, offloadable):
        self.__evaluate_params(millions_of_instructions, memory, data_in, data_out, offloadable)

        self._name = name
        self._millions_of_instructions = millions_of_instructions
        self._memory = memory
        self._data_in = data_in
        self._data_out = data_out
        self._in_edges = []
        self._out_edges = []
        self._off = offloadable
        self._execute = False
        self._offloading_site_name = ""
        self._policy = ()

        self.print_system()


    def get_name(cls):
        return cls._name


    def add_in_edge(cls, task):
        cls._in_edges.append(task)


    def add_out_edge(cls, task):
        cls._out_edges.append(task)


    def get_in_edges(cls):
        return cls._in_edges


    def get_out_edges(cls):
        return cls._out_edges


    def execute(cls):
        if cls._execute:
            return ExecutionErrorCode.EXE_NOK
        
        elif cls._in_edges:
            return ExecutionErrorCode.EXE_NOK
        
        else:
            for task in cls._out_edges:
                if not task.remove_in_edge(cls):
                    return ExecutionErrorCode.EXE_NOK

            cls._out_edges = []

            cls._execute = True

            return ExecutionErrorCode.EXE_OK


    def is_executed(cls):
        return cls._execute


    def is_offloadable(cls):
        return cls._off


    def print_dependencies(cls):
        #MdpLogger.write_log("################### " + cls._name + " DEPENDENCIES ###################")
    
        #MdpLogger.write_log("***INPUT DEPENDENCIES***")
        #for edge in cls._in_edges:
            #MdpLogger.write_log(edge.get_name())

        #MdpLogger.write_log("***OUTPUT DEPENDECIES***")
        #for edge in cls._out_edges:
            #MdpLogger.write_log(edge.get_name())

        #MdpLogger.write_log('\n\n')
        pass

    
    def print_system(cls):
        # MdpLogger.write_log("################### " + cls._name + " SYSTEM CONFIGURATION ###################")
        # MdpLogger.write_log("CPU: " + str(cls._millions_of_instructions) + " M cycles")
        # MdpLogger.write_log("Memory: " + str(cls._memory) + " Gb")
        # MdpLogger.write_log("Input data: " + str(cls._data_in) + " Kb")
        # MdpLogger.write_log("Output data: " + str(cls._data_out) + " Kb")
        # MdpLogger.write_log("Offloadable: Yes" if cls._off else "Offloadable: No\n")
        pass

    def remove_in_edge(cls, executed_task):
        if executed_task in cls._in_edges:
            cls._in_edges.remove(executed_task)
            return True
        else:
            return False


    def reset_exec_flag(cls):
        cls._execute = False
        cls._policy = ()
        cls._offloading_site_name = ""


    def get_data_in(cls):
        return cls._data_in


    def get_data_out(cls):
        return cls._data_out 


    def get_millions_of_instructions(cls):
        return cls._millions_of_instructions


    def get_memory(cls):
        return cls._memory


    def get_offloading_site(cls):
        return cls._offloading_site_name


    def get_offloading_policy(cls):
        return cls._policy


    def save_offloading_policy(cls, policy):
        cls._policy = policy


    def save_offloading_site(cls, name):
        if cls._execute:
            cls._offloading_site_name = name


    def __evaluate_params(cls, cpu, memory, data_in, data_out, offloadable):
        if cpu <= 0 or (type(cpu) is not float and type(cpu) is not int):
            raise ValueError("CPU should be positive float or integer!")

        if memory <= 0 or type(memory) is not int:
            raise ValueError("Memory should be positive integer!")

        if data_in <= 0 or (type(data_in) is not float and type(data_in) is not int):
            raise ValueError("Input data should be positive floatvor integer!")

        if data_out <= 0 or (type(data_out) is not float and type(data_out) is not int):
            raise ValueError("Output data should be positive float or integer!")

        if type(offloadable) is not bool:
            raise TypeError("Offloadable flag must be bool!")
