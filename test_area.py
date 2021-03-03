import sys
import socket
import pickle
import parameter
import pymysql
import json
'''
data = (('205958', '01_2102022059', 'close', 99, 98, 97, 102, 99, 100, 69, 71), 
('210000', '01_2102022059', 'close', 102, 101, 100, 101, 99, 99, 69, 70), 
('210002', '01_2102022059', 'close', 102, 96, 102, 100, 95, 100, 68, 66), 
('210004', '01_2102022059', 'close', 99, 97, 101, 97, 100, 101, 67, 67), 
('210006', '01_2102022059', 'close', 99, 100, 100, 97, 100, 99, 66, 71), 
('210008', '01_2102022059', 'close', 100, 99, 101, 102, 96, 101, 69, 71), 
('210010', '01_2102022059', 'close', 99, 100, 101, 100, 99, 100, 70, 74), 
('210013', '01_2102022059', 'close', 100, 98, 96, 99, 97, 96, 72, 72), 
('210015', '01_2102022059', 'close', 101, 98, 103, 102, 97, 101, 66, 69), 
('210017', '01_2102022059', 'close', 99, 99, 100, 99, 99, 100, 70, 68), 
('210019', '01_2102022059', 'close', 99, 98, 101, 98, 101, 103, 68, 71), 
('210021', '01_2102022059', 'close', 97, 100, 99, 99, 100, 101, 69, 69))

data_list = ""
one_sensor = []
data = list(data)
for i in  range(len(data)):
    temp = list(map(str, list(data[i])))
    one_sensor.append('/'.join(temp))
data_list = '|'.join(one_sensor)

number = str(sys.getsizeof(data_list))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((parameter.host, parameter.port))
sock.sendall('test'.encode())

sock.recv(1024)

sock.sendall(number.encode())

sock.recv(1024)

sock.sendall(data_list.encode())
'''

# combobox_data = {
#     "material" : ["material1", "material2", "material3"],
#     "process" : ["process1", "process2", "process3"],
#     "amount" : ["350", "550", "750"],
#     "gas" : ["gas1", "gas2", "gas3"]
# }

# with open('.\\json\\combobox.json', 'w') as json_file:
#     json.dump(combobox_data, json_file)

with open(parameter.json_path, 'r') as combo_json:
    combo_set = json.load(combo_json)
print(combo_set['material'])