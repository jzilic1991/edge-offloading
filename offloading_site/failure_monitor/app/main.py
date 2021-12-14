import sys

from socket_server import SocketServer


if __name__ == "__main__":
    SocketServer('localhost', 8000, sys.argv[len(sys.argv) - 1]).run()
