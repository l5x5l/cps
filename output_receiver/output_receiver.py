import socket

class outputReceiver:
    def __init__(self, host:str, port:str):
        self.sock = None
        self.host, self.port = host, port
        self.serv_addr = (self.host, self.port)

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.serv_addr)
        send_pkt = 'output_receiver'
        
    def send_msg(self):
        pass