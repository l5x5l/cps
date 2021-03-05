import parameter
import socket
import threading
import pymysql
import datetime
import utils
from packet import *
from data import Datas
import time as t


def server_furnace(sock:socket.socket, number:int, datas:Datas, q:list, dbconn, lock):
    dbcur = dbconn.cursor()
    process_id = ''
    is_running = False
    end_flag = False
    index = number - 1
    time_interval = parameter.time_interval

    #wait until recv process operation order
    print(datas.datas[index]['state'])
    while datas.datas[index]['state'] == 'on':

        for elem in q:
            if elem[0] == str(number):
                if elem[1] == 'start':
                    lock.acquire()
                    temp_list, heattime_list, staytime_list = [None] * 10, [None] * 10, [None] * 10
                    process_id, mete, manu, inp = elem[2:6]
                    count = int(elem[6])
                    temp_list[:count] = list(map(int, elem[7 : 7 + count]))
                    heattime_list[:count] = list(map(int, elem[7 + count : 7 + (2 * count)]))
                    staytime_list[:count] = list(map(int, elem[7 + (2 * count) : 7 + (3 * count)]))
                    gas = elem[-1]
                    sql = "INSERT INTO process(id, material, amount, manufacture, count, temper1, temper2, temper3, temper4, temper5, temper6, temper7, temper8, temper9, temper10, heattime1, heattime2, heattime3, heattime4, heattime5, heattime6, heattime7, heattime8, heattime9, heattime10, staytime1, staytime2, staytime3, staytime4, staytime5, staytime6, staytime7, staytime8, staytime9, staytime10,gas) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (process_id, mete, int(inp), manu, count, temp_list[0], temp_list[1], temp_list[2], temp_list[3], temp_list[4], temp_list[5], temp_list[6], temp_list[7], temp_list[8], temp_list[9], heattime_list[0], heattime_list[1], heattime_list[2], heattime_list[3], heattime_list[4], heattime_list[5], heattime_list[6], heattime_list[7], heattime_list[8], heattime_list[9], staytime_list[0], staytime_list[1], staytime_list[2], staytime_list[3], staytime_list[4], staytime_list[5], staytime_list[6], staytime_list[7], staytime_list[8], staytime_list[9], gas)
                    dbcur.execute(sql, val)
                    dbconn.commit()

                    send_pkt = packet_detail_setting(count, elem[7:7+count], elem[7 + count : 7 + (2 * count)], elem[7 + (2 * count) : 7 + (3 * count)], gas)
                    sock.sendall(send_pkt)

                    datas.working_furnace_data(number, process_id)

                    q.remove(elem)
                    lock.release()
                    break
                else:
                    lock.acquire()
                    print('[server] ignore msg in q : ' + str(elem[0]) + " : " + elem[1])
                    q.remove(elem)
                    lock.release()
        t.sleep(time_interval)


    #after furnace starts process
    while True:
        no_signal = True
        lock.acquire()
        for elem in q:
            if elem[0] == str(number):
                print('[server] ' + elem[0] + " " + elem[1])
                if elem[1] == 'end':
                    print('recv')
                    end_flag = True
                    sock.sendall(b'end signal')
                    break
                elif elem[1] == 'start':
                    sock.sendall(b'start signal')
                elif elem[1] == 'fix': #이 부분 수정필요
                    sock.sendall(b'fix signal')
                    temper, time = elem[2:]
                    send_pkt = packet_fix(temper, time)
                    sock.recv(1024)
                    print('[server] test line : 68')
                    sock.sendall(send_pkt)
                    #데이터베이스에 공정정보를 수정한 값으로 갱신
                    sql = "UPDATE process SET temperature = %s, time = %s WHERE id = %s"
                    val = (temper, time, process_id)
                    print('[server] test line : 73, 74')
                    dbcur.execute(sql, val)
                    dbconn.commit()
                    
                no_signal = False
                q.remove(elem)
        lock.release()

        if no_signal:
            sock.sendall(b'no_signal')

        #abnormal end of process
        if end_flag:
            sql = "UPDATE process SET output = %s WHERE id = %s"
            val = (int(1), process_id)
            dbcur.execute(sql, val)
            dbconn.commit()

            lock.acquire()
            datas.close_furnace_data(number)
            lock.release()
            break
        
        #recv sensor value from furnace
        pkt = sock.recv(1024)
        touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press, last = read_packet(pkt)

        #create current value which represent current time
        current = datetime.datetime.now()
        hour = '{:02d}'.format(current.hour)
        minute = '{:02d}'.format(current.minute)
        second = '{:02d}'.format(current.second)
        current_time = hour + minute + second

        #save sensor value to database
        sql = """INSERT INTO furnace%s(current, id, touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        val = (number, current_time, process_id, touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press)
        dbcur.execute(sql, val)
        dbconn.commit()

        #normal end of process
        if last == 'True':
            print('testline in thread 131')
            sock.sendall(b'end signal')
            sql = "UPDATE process SET output = %s WHERE id = %s"
            val = (int(0), process_id)
            dbcur.execute(sql, val)
            dbconn.commit()

            lock.acquire()
            datas.close_furnace_data(number)
            lock.release()
            break

    dbconn.close()
    sock.close()



def server_client(sock:socket.socket, datas:Datas, q:list, dbconn, lock):
    dbcur = dbconn.cursor()
    order_list = []
    for i in range(parameter.total_furnace):
        order_list.append([])
    temp = None
    number = None

    while True:
        print(temp)
        lock.acquire()
        data = datas.state_furnace()
        lock.release()

        recv_msg = sock.recv(1024).decode()
        recv_msg_list = recv_msg.split()
        if recv_msg_list[0] == 'esc':
            temp = None
            number = None
            sock.sendall(parameter.success_str.encode())
        elif recv_msg_list[0] == 'num':
            #[message example] num 1 -> select furnace1
            if temp is None:
                number = int(recv_msg_list[1])
                temp = order_list[number - 1]
                sock.sendall(parameter.success_str.encode())
            else:
                sock.sendall((parameter.error_str + '_num').encode())
        elif recv_msg_list[0] == 'base':
            if temp is not None and len(temp) == 0:
                base_element = recv_msg_list[1:]
                temp.append(base_element)
                sock.sendall(parameter.success_str.encode())
            else:
                sock.sendall((parameter.error_str + '_base').encode())
        elif recv_msg_list[0] == 'base_fix':
            if temp is not None and len(temp) == 1:
                prev_base = temp[-1]
                temp.pop()
                sock.sendall(parameter.success_str.encode())
            else:
                sock.sendall((parameter.error_str + '_base_fix').encode())
        elif recv_msg_list[0] == 'detail':
            if temp is not None and len(temp) == 1:
                detail_element = recv_msg_list[1:]
                temp.append(detail_element)

                #공정식별번호 생성
                now = datetime.datetime.now()
                month = '{:02d}'.format(now.month)
                day = '{:02d}'.format(now.day)
                hour = '{:02d}'.format(now.hour)
                minute = '{:02d}'.format(now.minute)
                process_id = '{:02d}'.format(int(number)) + '_' + str(now.year)[-2:] + month + day + hour + minute

                q_msg = [str(number), 'start', process_id] + temp[0] + temp[1]

                lock.acquire()
                q.append(q_msg)
                lock.release()

                sock.sendall(parameter.success_str.encode())
            else:
                sock.sendall((parameter.error_str + '_detail').encode())
        elif recv_msg_list[0] == 'detail_fix':
            if temp is not None and len(temp) == 2:
                prev_detail = temp[-1]
                temp.pop()
                sock.sendall(parameter.success_str.encode())
            else:
                sock.sendall((parameter.error_str + '_detail_fix').encode())
        elif recv_msg_list[0] == 'end':
            temp.clear()
            q_msg = [str(number), recv_msg_list[0]]

            lock.acquire()
            q.append(q_msg)
            lock.release()

            sock.sendall(parameter.success_str.encode())
        elif recv_msg_list[0] == 'init':
            number = int(recv_msg_list[1])
            print('thread 221 : ' + str(number))
            base_element = recv_msg_list[2:5]
            detail_element = recv_msg_list[5:]
            temp = order_list[number - 1]
            temp.append(base_element)
            temp.append(detail_element)
            temp = None

            sock.sendall(parameter.success_str.encode())
        else:
            sock.sendall((parameter.error_str + '_wrong msg type' + recv_msg_list[0]).encode())
    sock.close()

#dash앱에서 사용할 thread
def monitoring(values, times, lock:threading.Lock):
    now_working_process = ['-', '-', '-', '-', '-', '-', '-', '-']
    dbconn = pymysql.connect(host=parameter.host, user=parameter.user, password=parameter.password, database=parameter.db, charset=parameter.charset)
    dbcur = dbconn.cursor()

    sql = parameter.sql
    #sql = parameter.test_sql
    dbcur.execute(sql)
    processes = dbcur.fetchall()

    for process in processes:
        number = int(process[0][:2])

        if now_working_process[number - 1] == '-':
            now_working_process[number - 1] = process[0]
        else:
            #만약 해당 열처리로에 2개 이상 작동중인 공정이 발견될 경우(비정상, 일반적인 경우에 발견되어서는 안됨), 이후 공정으로 설정
            if int(process[0].split('_')[-1]) >= int(now_working_process[number - 1].split('_')[-1]):
                now_working_process[number - 1] = process[0]
            else:
                sql = "UPDATE process SET output = %s WHERE id = %s"
                val = (int(2), process[0])
                dbcur.execute(sql, val)
                dbconn.commit()

        sql = """select * from furnace""" + str(number) +  """ where id = '""" + process[0] + """' order by current desc limit 10"""
        dbcur.execute(sql)
        sensors = list(dbcur.fetchall())
        sensors.reverse()

        lock.acquire()
        values[int(number) - 1] = [one_step[2:] for one_step in sensors]
        times[int(number) - 1] = [utils.get_time(one_step[0]) for one_step in sensors]
        lock.release()

    while True:
        dbconn.commit()
        sql = parameter.sql
        #sql = parameter.test_sql
        dbcur.execute(sql)
        processes = dbcur.fetchall()

        print('testline 393')
        print(processes)

        for process in processes:
            dbconn.commit()
            number = int(process[0][:2])
            index = number - 1
            sql = """select * from furnace""" + str(number) +  """ where id = '""" + process[0] + """' order by current desc limit 1"""
            dbcur.execute(sql)
            sensors = list(dbcur.fetchall())

            
            #기존 기록되었던 공정에서 다른 공정으로 변경된 경우 그래프 갱신을 위해 데이터 초기화
            if now_working_process[index] != process[0]:
                print('testline 399')
                now_working_process[index] = process[0]
                values[index] = []
                times[index] = []
            

            #진행중인 공정이나, 아직 센서값이 없는 경우(막 시작한 경우)
            if len(sensors) == 0:
                t.sleep(1)
                continue

            #진행중인 공정이나, 아직 센서값이 업데이트되지 않은 경우(마지막 시간과 동일한 경우)
            if len(times[index]) != 0  and times[index][-1] == utils.get_time(sensors[0][0]):
                t.sleep(1)
                continue

            lock.acquire()
            if len(values[index]) >= 10:
                values[index][:-1] = values[index][1:]
                times[index][:-1] = times[index][1:]
                values[index][-1] = sensors[0][2:]
                times[index][-1] = utils.get_time(sensors[0][0])
            else:
                values[index].append(sensors[0][2:])
                times[index].append(utils.get_time(sensors[0][0]))
            lock.release()

        t.sleep(parameter.time_interval)

    dbconn.close()


