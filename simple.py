import socket
import device
import data
import parameter

class Simple(device.Device):
    def __init__(self, host:str, port:int):
        self.host = host
        self.port = port
        self.serv_addr = (self.host, self.port)
        self.sock = None
        self.sensors = data.Sensors(parameter.total_furnace)


    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.serv_addr)
        send_pkt = b'simple'
        self.send_msg(send_pkt, self.sock)


    def close(self):
        self.sock.close()


    def simple_first_recv(self):    

        for i in range(parameter.total_furnace):
            sensors = self.sock.recv(2048)
            sensors = sensors.decode()
            if sensors == 'not working':
                self.send_msg('recv', self.sock)
                continue
            elif sensors == 'not yet':
                self.send_msg('recv', self.sock)
                continue

            steps = sensors.split('/')
            #pop 이유는 마지막 원소가 '' 이기 때문
            steps.pop()
            self.sensors.set_first(steps, i)
            self.send_msg('recv', self.sock)


    def simple_recv_sensors(self):
        sensor_msg = self.recv_msg(self.sock)
        furnace_sensor = sensor_msg.split('/')
        #pop 이유는 마지막 원소가 '' 이기 때문
        furnace_sensor.pop()
        

        '''
        for i, sensor in enumerate(furnace_sensor):
            print(str(i+1) + ' :', end = ' ' )
            print(sensor)
        '''

        self.sensors.renew(furnace_sensor)
        '''
        print('---------------------------------')
        for i in range(parameter.total_furnace):
            sen = self.sensors.get_sensor(i + 1)
            print(sen)
        '''

            
    def confirm_data(self):
        for i in range(parameter.total_furnace):
            print(str(i+1) + '----------------------------')
            temp = self.sensors.get_sensor(i + 1)
            print(temp)

    


'''
        
simple = Simple(parameter.host, parameter.port)
simple.connect()
simple.simple_first_recv()
simple.confirm_data()
while True:
    simple.simple_recv_sensors()
simple.close()
'''