import socket
import threading
import time
import pymysql
import thread
import data
import parameter
import pickle
from device import Device

class Server(Device):
    def __init__(self, addr:str, port:int, total_furncae:int, maximum:int):
        print('[server] setup server')
        self.addr = addr
        self.port = port
        self.serv_addr = (self.addr, self.port)
        self.datas = data.Datas(total_furncae)
        self.q = []
        
        #test용
        #self.datas.for_test()

        self.lock = threading.Lock()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.serv_addr)
        self.sock.listen(maximum)


    def connect_db(self, user:str, password:str, db:str, charset:str):
        dbconn = pymysql.connect(host=self.addr, user = user, password = password, database = db, charset = charset)
        return dbconn


    def connect(self) -> socket.socket:
        conn_sock, client_addr = self.sock.accept()
        print('[server] connect with ' + str(client_addr[0]))

        confirm_msg = self.recv_msg(conn_sock).split()
        print('[server] connect device is ' + confirm_msg[0])

        return conn_sock, confirm_msg



serv = Server('165.246.44.133', 3050, parameter.total_furnace, 10)
conn_sock, confirm_msg = serv.connect()
conn_sock.sendall('confirm'.encode())

num = conn_sock.recv(1024).decode()
print(num)
conn_sock.sendall('confirm'.encode())

msg = conn_sock.recv(int(num))
msg = msg.decode()

sensors = []
for time_step in msg.split('|'):
    sensors.append(time_step.split('/'))

print(sensors)