import socket

class OutputReceiver:
    def __init__(self, host:str, port:str):
        self.sock = None
        self.host, self.port = host, port
        self.serv_addr = (self.host, self.port)

        self.process_info = {}

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.serv_addr)
        send_pkt = 'output_receiver'
        
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