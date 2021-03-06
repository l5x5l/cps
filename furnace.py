import socket
import random
import parameter
import time
from packet import *
from device import Device
import sys
import datetime

class Furnace(Device):
    def __init__(self, host, port, number):
        """
        number : furnace number
        index : used for setting sensor's temperature
        tempers : temperature list
        heattimes : 승온 시간들
        staytimes : 현 온도를 유지하는 시간들
        mean : 가상의 센서값을 만들 때 사용 (평균)
        sd : 가상의 센서값을 만들 때 사용 (표준편차)
        inclication : 가상의 센서값을 만들 때 사용, 승온시 온도의 상승폭을 나타냄
        start_time : 공정의 시작 시간
        process_time : 공정의 총 시간
        current_time : 공정의 현 시간
        gas : 공정에 사용되는 가스의 종류
        """
        self.number = number
        self.host = host
        self.port = port
        self.serv_addr = (host, port)
        self.sock = None

        self.index = 0
        self.tempers = []
        self.heattimes = []
        self.staytimes = []

        self.mean = 0
        self.sb = None
        self.inclination = None
        self.start_time = None
        self.process_time = None
        self.current_time = None
        self.gas = None


    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.serv_addr)  
        print('[furnace] connect with server')
        self.send_msg('furnace ' + str(self.number), self.sock)


    def set_mean(self):
        if self.index >= len(self.tempers):
            return
        else:
            if self.current_time < self.heattimes[self.index]:  #승온
                if self.inclination is None:
                    self.inclination = self.tempers[0] / self.heattimes[0]
                if self.index == 0: #first heattime
                    self.mean = int(self.inclination * self.current_time)
                    pass
                else:   
                    self.mean = self.tempers[self.index - 1] + int(self.inclination * (self.current_time - self.staytimes[self.index - 1]))

            elif self.current_time < self.staytimes[self.index]:    #유지
                #self.mean = self.tempers[self.index]
                pass
            else:      #승온
                self.index += 1
                if self.index >= len(self.tempers):
                    return
                else:
                    self.inclination = (self.tempers[self.index] - self.tempers[self.index - 1]) / (self.heattimes[self.index] - self.staytimes[self.index - 1])
                    self.mean = self.tempers[self.index - 1] + int(self.inclination * (self.current_time - self.staytimes[self.index - 1]))
            


    #실제 센서값을 재현하기 위해 사용
    def get_sensors(self):
        #try:
        temp = []
        self.set_mean()
        for i in range(6):
            temp.append(int(random.gauss(self.mean, self.sb)))
        temp1, temp2, temp3, temp4, temp5, temp6 = temp
        touch = 'close'

        flow = int(random.gauss(70, 2))
        press = int(random.gauss(70, 2))
        '''
        except Exception as e:
            print('[furnace] error ', e)
            return
        '''
        
        #print('[furnace] test line 49')
        #print(str(self.process_time) + ' : ' + str(self.current_time))

        if self.process_time <= self.current_time:
            isLast = 'True'
        else:
            isLast = 'False'

        return touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press, isLast


    def furnace_main(self):
        signal = self.recv_msg(self.sock)
        print('[furnace] ' + signal)
        if signal == 'end signal':
            self.close()
        elif signal == 'fix signal':    #need to fix
            self.send_msg('fix confirm', self.sock)
            self.modify()


        touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press, isLast = self.get_sensors()
        send_pkt = packet_sensor(touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press, isLast)
        self.send_msg(send_pkt, self.sock)


        if isLast == 'True':
            self.close()

        self.current_time = int((datetime.datetime.now() - self.start_time).total_seconds())

        time.sleep(parameter.time_interval)


    def close(self):
        self.sock.close()
        exit()


    def preprocessing(self):
        recv_pkt = self.recv_msg(self.sock)
        print('[furnace-test line 122] recv pkt' + recv_pkt)
        count, temp, heattime, staytime, gas = read_packet(recv_pkt)
        
        print('[furnace-test line 125] recv pkt')
        print(temp)

        self.process_setting(count, temp, heattime, staytime, gas)


    def modify(self):   #need to fix
        recv_pkt = self.recv_msg(self.sock)
        temp, time = read_packet(recv_pkt)
        self.modify_setting(temp, time)


    def process_setting(self, count, temp, heattime, staytime, gas):
        totaltime = 0
        self.tempers = temp
        self.heattimes.append(heattime[0])
        self.staytimes.append(self.heattimes[0] + staytime[0])
        totaltime += heattime[0]
        totaltime += staytime[0]
        for i in range(1, count):
            self.heattimes.append(self.staytimes[-1] + heattime[i])
            self.staytimes.append(self.heattimes[-1] + staytime[i])
            totaltime += heattime[i]
            totaltime += staytime[i]  
            
        self.process_time = totaltime
        self.current_time = 0
        self.start_time = datetime.datetime.now()
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

furnace.close()
