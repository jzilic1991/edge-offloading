import sys


class Logger:

    def __init__ (self, filename, gate, action):
        self._file = filename
        self._gate = bool(gate)
        self._action = action
        self._file_handler = open(self._file, self._action)


    def enable (cls):
        cls._gate = True


    def disable (cls):
        cls._gate = False


    def update_action (cls, action):
        cls._action = action
        cls._file_handler.close()
        cls._file_handler = open(cls._file, cls._action)


    def w (cls, text):
        if cls._gate:
            cls._file_handler.write(text + "\n")

    
    def p (cls, text):
        if cls._gate:
            print (text + "\n", file = sys.stdout)
            cls._file_handler.write(text + "\n")
