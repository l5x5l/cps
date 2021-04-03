import datetime
import parameter
from PyQt5 import QtCore

def get_working_process(dbcur):
    """
    dbcur(sql connector cursor)
    return : working process id list, indicates furance's wokring process
    ex ['01_00000000', '-', '-', '-', '05_00000000', '-', '-', '-']
    """
    sql = parameter.sql
    dbcur.execute(sql)
    processes = dbcur.fetchall()   
    working_process = ['-'] * parameter.total_furnace
    for process in processes:
        number = int(process[0][:2])
        working_process[number - 1] = process[0]

    return working_process

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


def get_total_time(heattimes, staytimes):
    total_time = 0
    for i in range(len(heattimes)):
        total_time += int(heattimes[i])
        total_time += int(staytimes[i])
    return total_time

def sleep(n):
    """
    wait function
    """
    loop = QtCore.QEventLoop()
    QtCore.QTimer.singleShot(int(n * 1000), loop.quit)
    loop.exec_()