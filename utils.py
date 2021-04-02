import datetime

def get_elapsed_time(start_time):
    """
    공정 소요 시간을 계산하는 함수\n
    start_time(str or datetime.datetime) : "%m/%d/%y %H:%M:%S"형식을 가지고 있으며, 본 함수를 실행할 때의 now time에서 start_time을 뺀 시간을 초단위로 리턴\n
    return type : int
    """
    if type(start_time) is str:
        output = int((datetime.datetime.now().replace(microsecond=0) - datetime.datetime.strptime(start_time, "%m/%d/%y %H:%M:%S")).total_seconds())
    else:
        output = int((datetime.datetime.now().replace(microsecond=0) - start_time).total_seconds())

    return output

def make_current():
    """
    create current time form "hhmmss"\n
    [example] 2pm 30minute 55seconds => 143055\n
    return value(str) : current time\n
    """
    current = datetime.datetime.now()
    hour = '{:02d}'.format(current.hour)
    minute = '{:02d}'.format(current.minute)
    second = '{:02d}'.format(current.second)
    current_time = hour + minute + second
    return current_time

def change_current_to_seconds(current:str):
    """
    change time form "hhmmss" to seconds\n
    current(str) : current time string, ex) 121036\n
    return value(int) : total seconds of current\n
    [example] 121036 -> 43836 seconds\n
    """
    current = int(current)
    temp = (current // 10000) * 3600
    temp += (current % 10000) // 100 * 60
    temp += (current % 100)
    return temp

def make_process_id(number:int):
    """
    create process id\n
    number(int) : furnace number\n
    return value(str) : process id\n
    """
    now = datetime.datetime.now()
    month = '{:02d}'.format(now.month)
    day = '{:02d}'.format(now.day)
    hour = '{:02d}'.format(now.hour)
    minute = '{:02d}'.format(now.minute)
    process_id = '{:02d}'.format(int(number)) + '_' + str(now.year)[-2:] + month + day + hour + minute

    return process_id

def extract_detail_option(elem:list):
    temp_list, heattime_list, staytime_list = [None] * 10, [None] * 10, [None] * 10
    recv_process_id, mete, manu, inp = elem[2:6]
    count = int(elem[6])
    temp_list[:count] = list(map(int, elem[7 : 7 + count]))
    heattime_list[:count] = list(map(int, elem[7 + count : 7 + (2 * count)]))
    staytime_list[:count] = list(map(int, elem[7 + (2 * count) : 7 + (3 * count)]))
    gas = elem[-1]

    return recv_process_id, mete, manu, inp, count, temp_list, heattime_list, staytime_list, gas

def get_total_time(heattimes, staytimes):
    total_time = 0
    for i in range(len(heattimes)):
        total_time += int(heattimes[i])
        total_time += int(staytimes[i])
    return total_time