def packet_number_option(number:int, option:str):
    temp_str = 'np {0} {1}'.format(str(number), option)
    temp_byte = temp_str.encode()
    return temp_byte

def packet_init_set_process(elem:str, manu:str, amount:int):
    temp_str = 'isp {0} {1} {2}'.format(elem, manu, str(amount))
    temp_byte = temp_str.encode()
    return temp_byte

def packet_detail_set_process(temp:int, time:int, gas:str):
    temp_str = 'dsp {0} {1} {2}'.format(str(temp), str(time), gas)
    temp_byte = temp_str.encode()
    return temp_byte

def packet_sensor(touch:str, temp1:int, temp2:int, temp3:int, temp4:int, temp5:int, temp6:int, flow:int, press:int, last:str):
    temp_str = 'sen {0} {1} {2} {3} {4} {5} {6} {7} {8} {9}'.format(touch, str(temp1), str(temp2), str(temp3), str(temp4), str(temp5), str(temp6), str(flow), str(press), last)
    temp_byte = temp_str.encode()
    return temp_byte

def packet_fix(temper:int, time:int):
    temp_str = 'fix {0} {1}'.format(str(temper), str(time))
    temp_byte = temp_str.encode()
    return temp_byte

def packet_detail_setting(count:int, tempers:list, heattimes:list, staytimes:list, gas:str):
    temp = '_'.join(tempers)
    heattime = '_'.join(heattimes)
    staytime = '_'.join(staytimes)
    temp_str = "ds {0} {1} {2} {3} {4}".format(str(count), temp, heattime, staytime, gas)
    temp_byte = temp_str.encode()
    return temp_byte

##UI_custom에 있는 방식으로 교체 필요, 일단 아직은 안함
## + 추가적으로, None값을 전달하는 방식으로 mariadb에 null값을 넣을 수 있다.

'''
value = None
cursor.execute("INSERT INTO table (`column1`) VALUES (%s)", (value,))
'''

def read_packet(packet):
    if type(packet) is bytes:
        packet = packet.decode().split()
    elif type(packet) is str:
        packet = packet.split()

    if packet[0] == 'np':
        number, option = packet[1:]
        return int(number), option
    elif packet[0] == 'isp':
        elem, manu, amount = packet[1:]
        return elem, manu, int(amount)
    elif packet[0] == 'dsp':
        temp, time, gas = packet[1:]
        return int(temp), int(time), gas
    elif packet[0] == 'sen':
        touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press, last = packet[1:]
        return touch, int(temp1), int(temp2), int(temp3), int(temp4), int(temp5), int(temp6), int(flow), int(press), last
    elif packet[0] == 'fix':
        temper, time = packet[1:]
        return int(temper), int(time)
    elif packet[0] == 'ds':
        print(packet[1:])
        count, temp, heattime, staytime, gas = packet[1:]
        temp_list = temp.split('_')
        heattime_list = heattime.split('_')
        staytime_list = staytime.split('_')
        
        temp_list = list(map(int, temp_list))
        heattime_list = list(map(int, heattime_list))
        staytime_list = list(map(int, staytime_list))

        return int(count), temp_list, heattime_list, staytime_list, gas