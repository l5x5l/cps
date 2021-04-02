import socket
import threading
import time
import pymysql
import thread
import data
import parameter
from device import Device

class Server(Device):
    def __init__(self, addr:str, port:int, total_furnace:int, maximum:int):
        print('[server] setup server')
        self.addr = addr
        self.port = port
        self.serv_addr = (self.addr, self.port)
        self.datas = data.Datas(total_furnace)
        self.order_queue = []
        self.normal_end_queue = []
        
        for i in range(total_furnace):
            self.order_queue.append([])

        self.specific_furnace_lock = []
        for i in range(parameter.total_furnace):
            self.specific_furnace_lock.append(threading.Lock())

        self.end_queue_lock = threading.Lock()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.serv_addr)
        self.sock.listen(maximum)


    def connect_db(self, user:str, password:str, db:str, charset:str):
        dbconn = pymysql.connect(host=self.addr, user = user, password = password, database = db, charset = charset)
        return dbconn


    def connect(self):
        conn_sock, client_addr = self.sock.accept()
        print('[server] connect with ' + str(client_addr[0]))

        confirm_msg = self.recv_msg(conn_sock).split()
        print('[server] connect device is ' + confirm_msg[0])

        return conn_sock, confirm_msg


    def start_thread(self, conn_sock, confirm_msg):
        confirm = confirm_msg
        if confirm[0] == 'furnace':
            number = int(confirm[1])    #furnace number
            self.datas.on_furnace_data(number)
            dbconn = self.connect_db(parameter.user, parameter.password, parameter.db, parameter.charset)
            t = threading.Thread(target=thread.server_furnace, args=(conn_sock, number, self.datas, self.order_queue[number - 1], dbconn, self.specific_furnace_lock[number - 1], self.normal_end_queue, self.end_queue_lock))
            t.start()
        elif confirm[0] == 'client':
            dbconn = self.connect_db(parameter.user, parameter.password, parameter.db, parameter.charset)
            t = threading.Thread(target=thread.server_client, args=(conn_sock, self.datas, self.order_queue, dbconn, self.specific_furnace_lock))
            t.start()


# serv = Server(parameter.host, parameter.port, parameter.total_furnace, parameter.maximum_client)
# while True:
#     conn_sock, confirm_msg = serv.connect()
#     serv.start_thread(conn_sock, confirm_msg)
    