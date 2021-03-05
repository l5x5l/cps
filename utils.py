import datetime

def get_time(current:str):
    """
    change time form "hhmmss" to seconds
    current(str) : current time string, ex) 121036
    return value(int) : total seconds of current
    [example] 121036 -> 43836 seconds
    """
    current = int(current)
    temp = (current // 10000) * 3600
    temp += (current % 10000) // 100 * 60
    temp += (current % 100)
    return temp

def make_process_id(number:str):
    """
    create process id
    number(str) : furnace number
    return value(str) : process id
    """
    now = datetime.datetime.now()
    month = '{:02d}'.format(now.month)
    day = '{:02d}'.format(now.day)
    hour = '{:02d}'.format(now.hour)
    minute = '{:02d}'.format(now.minute)
    process_id = '{:02d}'.format(int(number)) + '_' + str(now.year)[-2:] + month + day + hour + minute

    return process_id