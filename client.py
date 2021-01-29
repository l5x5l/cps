import socket
from device import Device
import parameter
from packet import *
import time as t

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


    #ui와 연동시 input을 사용해 입력받는 부분을 대체하여 사용될 예정 (지금은 사용 x)
    def set_param(self, param, value):
        param = value


    def client_main(self):
        state_msg = self.recv_msg(self.sock)
        print('current furnaces state\n' +  state_msg)
        number = input('[client] select furnace number : ')
        option = input('[client] select option < end | start | fix > : ')
        num_opt  = number + ' ' + option
        self.send_msg(num_opt, self.sock)

        check_msg = self.recv_msg(self.sock)
        print('[client] ' + check_msg)

        if check_msg.startswith('Error'):
            return
        
        if option == 'start':
            self.start_option()
        elif option == 'fix':
            self.fix_option()
        elif option == 'end':
            self.end_option()

    def start_option(self):
        print('[client] start process')
        values = input('[client] input <재료 공정 투입량> : ').split()
        while (len(values) != 3):
            print('[client] wrong input')
            values = input('[client] input <재료 공정 투입량> : ').split()

        elem, manu, amount = values
        send_pkt = packet_init_set_process(elem, manu, int(amount))
        self.send_msg(send_pkt, self.sock)
        recv_pkt = self.recv_msg(self.sock)
        temp, time, gas = read_packet(recv_pkt)
        
        an = input('[client] 값을 수동으로 변경하시겠습니까? y/n')
        while not(an == 'y' or an == 'n'):
            print('[client] wrong input')
            an = input('[client] 값을 수동으로 변경하시겠습니까? y/n')
        if an == 'y':
            values = input('[client] input <온도 시간 가스> : ').split()
            temp, time, gas = values
        
        send_pkt = packet_detail_set_process(int(temp), int(time), gas)
        self.send_msg(send_pkt, self.sock)


    def end_option(self):
        print('[client] end process')


    def fix_option(self):
        print('[client] fix process')
        values = input('[client] input <온도 시간> : ').split()
        temp, time, gas = values
        send_pkt = packet_fix(int(temp), int(time))
        self.send_msg(send_pkt, self.sock)


    def client_thread(self):
        pass

    def close(self):
        self.sock.close()

client = Client(parameter.host, parameter.port)
client.connect()
while True:
    client.client_main()
    t.sleep(1)
client.close()