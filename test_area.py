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

#sql = "INSERT INTO process(id, material, amount, manufacture, count, temper1, temper2, temper3, temper4, temper5, temper6, temper7, temper8, temper9, temper10, heattime1, heattime2, heattime3, heattime4, heattime5, heattime6, heattime7, heattime8, heattime9, heattime10, staytime1, staytime2, staytime3, staytime4, staytime5, staytime6, staytime7, staytime8, staytime9, staytime10,gas) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#sql = "UPDATE process SET temperature = %s, time = %s WHERE id = %s"

sql = "UPDATE process SET material = %s, amount = %s, manufacture = %s, count = %s, temper1 = %s, temper2 = %s, temper3 = %s, temper4 = %s, temper5 = %s, temper6 = %s, temper7 = %s, temper8 = %s, temper9 = %s, temper10 = %s, heattime1 = %s, heattime2 = %s, heattime3 = %s, heattime4 = %s, heattime5 = %s, heattime6 = %s, heattime7 = %s, heattime8 = %s, heattime9 = %s, heattime10 = %s, staytime1 = %s, staytime2 = %s, staytime3 = %s, staytime4 = %s, staytime5 = %s, staytime6 = %s, staytime7 = %s, staytime8 = %s, staytime9 = %s, staytime10 = %s, gas = %s WHERE id = %s"
val = (mete, int(inp), manu, count, temp_list[0], temp_list[1], temp_list[2], temp_list[3], temp_list[4], temp_list[5], temp_list[6], temp_list[7], temp_list[8], temp_list[9], heattime_list[0], heattime_list[1], heattime_list[2], heattime_list[3], heattime_list[4], heattime_list[5], heattime_list[6], heattime_list[7], heattime_list[8], heattime_list[9], staytime_list[0], staytime_list[1], staytime_list[2], staytime_list[3], staytime_list[4], staytime_list[5], staytime_list[6], staytime_list[7], staytime_list[8], staytime_list[9], gas, process_id)
