import socket
import random
import parameter
import time
from packet import *
from device import Device
import sys

class Furnace(Device):
    def __init__(self, host, port, number):
        self.number = number
        self.host = host
        self.port = port
        self.serv_addr = (host, port)
        self.sock = None

        self.mean = None
        self.sb = None
        self.updraft = None
        #여기서 process_time은 실시간이 아니라 반복횟수로 여긴다. (추후 시간으로 수정 예정)
        self.process_time = None
        self.current_time = None
        self.gas = None


    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.serv_addr)  
        print('[furnace] connect with server')
        self.send_msg('furnace ' + str(self.number), self.sock)


    #실제 센서값을 재현하기 위해 사용
    def get_sensors(self):
        try:
            temp = []
            for i in range(6):
                temp.append(int(random.gauss(self.mean, self.sb)))
            temp1, temp2, temp3, temp4, temp5, temp6 = temp
            touch = 'close'

            flow = int(random.gauss(70, 2))
            press = int(random.gauss(70, 2))
        except Exception as e:
            print('[furnace] error ', e)
            return
        
        print('[furnace] test line 49')
        print(str(self.process_time) + ' : ' + str(self.current_time))

        if self.process_time < self.current_time:
            isLast = 'True'
        else:
            isLast = 'False'

        return touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press, isLast


    def furnace_main(self):
        signal = self.recv_msg(self.sock)
        print('[furnace] ' + signal)
        if signal == 'end signal':
            self.close()
        elif signal == 'fix signal':
            self.send_msg('fix confirm', self.sock)
            self.modify()


        touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press, isLast = self.get_sensors()
        send_pkt = packet_sensor(touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press, isLast)
        self.send_msg(send_pkt, self.sock)

        print('[furnace] test line 70 ' + isLast)
        if isLast == 'True':
            print('[furnace] test line')
            self.close()

        self.current_time += 1 #임의로 설정
        time.sleep(parameter.time_interval)


    def close(self):
        self.sock.close()
        exit()


    def preprocessing(self):
        recv_pkt = self.recv_msg(self.sock)
        print('[furnace-test line 80] recv pkt' + recv_pkt)
        temp, time, gas = read_packet(recv_pkt)
        
        self.process_setting(temp, time, gas)


    def modify(self):
        recv_pkt = self.recv_msg(self.sock)
        temp, time = read_packet(recv_pkt)
        self.modify_setting(temp, time)


    def process_setting(self, temp, time, gas):
        self.mean = temp
        self.process_time = time
        self.current_time = 0
        self.sb = 2
        self.gas = gas


    def modify_setting(self, temp, time):
        self.mean = temp
        self.process_time = time


furnace = Furnace('165.246.44.133', 3050, sys.argv[1])
furnace.connect()
furnace.preprocessing()
while True:
    furnace.furnace_main()
