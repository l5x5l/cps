import socket

class Client:
    def __init__(self, host:str, port:int):
        self.host = host
        self.port = port
        self.serv_addr = (self.host, self.port)
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.serv_addr)
        send_pkt = 'client'
        self.send_msg(send_pkt)

    def recv_msg(self):
        msg = self.sock.recv(1024)
        return msg.decode()

    def send_msg(self, msg):
        if type(msg) is bytes:
            self.sock.sendall(msg)
        elif type(msg) is str:
            msg = msg.encode()
            self.sock.sendall(msg)

    def close(self):
        self.sock.close()
