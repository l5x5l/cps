import socket
from abc import *

class Device(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self):
        pass


    @abstractmethod
    def connect(self):
        pass


    def recv_msg(self, sock:socket.socket):
        msg = sock.recv(1024)
        return msg.decode()


    def send_msg(self, msg, sock:socket.socket):
        if type(msg) is bytes:
            sock.sendall(msg)
        elif type(msg) is str:
            msg = msg.encode()
            sock.sendall(msg)
