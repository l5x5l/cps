import datetime

def extract_detail_option(elem:list):
    """
    공정 세부 설정값 추출
    """
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

def change_process_option_to_str(process_setting:list):
    """
    processId, mete, manu, inp, count, tempList, heattimeList, staytimeList, gas를 하나의 str로 변환\n
    tempList, heattimeList, staytimeList는 10의 크기를 가지며, count의 개수만큼 실제 값을 가지며 10-count만큼은 Null값을 가지고 있다.\n
    ['02_2104031519', 'material3', 'process3', '500', 2, [150, 300, None, None, None, None, None, None, None, None], [15, 15, None, None, None, None, None, None, None, None], [15, 15, None, None, None, None, None, None, None, None], 'gas3']
    """
    count = process_setting[4]
    for i in range(len(process_setting)):
        if type(process_setting[i]) is list:
            process_setting[i] = '-'.join(list(map(str, process_setting[i][:count])))
        elif type(process_setting[i]) is int:
            process_setting[i] = str(process_setting[i])
    
    return '/'.join(process_setting)


def check_process(dbcur, process_id):
    """
    check same process already exists
    dbcur(database connector's cursor)
    process_id(str) : process identifier

    return : if process_id already exist, return False, else return True
    """
    sql = """select * from process where id = '""" + process_id + """'"""
    dbcur.execute(sql)
    result = dbcur.fetchall()

    return len(result) == 0