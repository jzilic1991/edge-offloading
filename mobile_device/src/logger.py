class Logger(object):

    file_handler = open("logs/simulation_log.txt", 'w')

    @staticmethod
    def w (text):
        if True:
            Logger.file_handler.write(text + "\n")
