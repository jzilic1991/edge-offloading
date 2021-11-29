import sys

from socket_server import SocketServer


if __name__ == "__main__":
    SocketServer('localhost', 8000).run()
