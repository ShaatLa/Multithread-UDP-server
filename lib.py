import socket
import logging
import random


class SocketClass(object):
    """Class for simplyfication use of sockets"""

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self._sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=0)

    def send_data(self, data):
        self._sock.send(data.encode('utf-8'))

    def recv_data(self, buffersize=1024):
        data_binary = self._sock.recv(buffersize)
        data = data_binary.decode('utf-8')
        return data

    def settimeout(self, num):
        self._sock.settimeout(num)

    def close(self):
        self._sock.close()
        log.info('Connection closed.')


def log():
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger("dispatcher")
    log.setLevel(logging.DEBUG)
    return log


def break_calculator():
    """Calculator crash imitation function"""
    number = random.randrange(1, 100)
    return number
