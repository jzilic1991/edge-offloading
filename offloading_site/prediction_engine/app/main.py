import warnings

from socket_server import SocketServer


if __name__ == "__main__":
    warnings.filterwarnings ('ignore', category = DeprecationWarning)
    SocketServer('localhost', 8001).run()
