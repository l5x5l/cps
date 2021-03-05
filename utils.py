import datetime

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