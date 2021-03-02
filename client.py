import socket
from device import Device
import parameter
from packet import *
import time as t
import threading
import thread

class Client(Device):
    def __init__(self, host:str, port:int):
        self.host = host
        self.port = port
        self.serv_addr = (self.host, self.port)
        self.sock = None


    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.serv_addr)
        send_pkt = 'client'
        self.send_msg(send_pkt, self.sock)

    def close(self):
        self.sock.close()
