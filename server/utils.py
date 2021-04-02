import datetime

def extract_detail_option(elem:list):
    temp_list, heattime_list, staytime_list = [None] * 10, [None] * 10, [None] * 10
    recv_process_id, mete, manu, inp = elem[2:6]
    count = int(elem[6])
    temp_list[:count] = list(map(int, elem[7 : 7 + count]))
    heattime_list[:count] = list(map(int, elem[7 + count : 7 + (2 * count)]))
    staytime_list[:count] = list(map(int, elem[7 + (2 * count) : 7 + (3 * count)]))
    gas = elem[-1]

    return recv_process_id, mete, manu, inp, count, temp_list, heattime_list, staytime_list, gas

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