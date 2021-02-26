import parameter
import socket
import threading
import pymysql
import datetime
from packet import *
from data import Datas
import time as t
from simple import Simple


def server_furnace(sock:socket.socket, number:int, datas:Datas, q:list, dbconn, lock):
    dbcur = dbconn.cursor()
    process_id = ''
    is_running = False
    end_flag = False
    index = number - 1
    time_interval = parameter.time_interval

    #연결한 열처리로가 작업을 시작할 때까지 대기후 작업을 시작하는 신호를 수신한 경우 공정 설정값 전송
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

                    send_pkt = packet_detail_set_process(100, 100, gas)
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

    print(datas.datas[index]['state'])

    print('testline thread 51')
    print(q)


    #열처리로가 작업을 시작한 이후 실행되는 부분
    while True:
        no_signal = True
        lock.acquire()
        for elem in q:
            if elem[0] == str(number):
                print('[server] ' + elem[0] + " " + elem[1])
                if elem[1] == 'end':
                    end_flag = True
                    sock.sendall(b'end signal')
                    break
                elif elem[1] == 'start':
                    sock.sendall(b'start signal')
                elif elem[1] == 'fix':
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

        print('testline 86')
        print(no_signal)
        if no_signal:
            sock.sendall(b'no_signal')

        #비정상 종료 (클라이언트에서 종료 신호를 보낸 경우)
        if end_flag:
            sql = "UPDATE process SET output = %s WHERE id = %s"
            val = (int(1), process_id)
            dbcur.execute(sql, val)
            dbconn.commit()

            lock.acquire()
            datas.close_furnace_data(number)
            lock.release()
            break
        
        #센서값을 열처리로로부터 받아옴
        pkt = sock.recv(1024)
        touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press, last = read_packet(pkt)
        #print('[server] recv sensor values\n')
        #print(touch + " : " + str(temp1) + " : " + str(temp2) + " : " + str(temp3) + " : " + str(temp4) + " : " + str(temp5) + " : " + str(temp6) + " : " + str(flow) )

        #현재 시각을 나타내는 current 생성(db의 primary key)
        current = datetime.datetime.now()
        hour = '{:02d}'.format(current.hour)
        minute = '{:02d}'.format(current.minute)
        second = '{:02d}'.format(current.second)
        current_time = hour + minute + second

        #센서값을 db에 저장
        sql = """INSERT INTO furnace%s(current, id, touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        val = (number, current_time, process_id, touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press)
        dbcur.execute(sql, val)
        dbconn.commit()

        #정상 종료
        if last == 'True':
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
    while True:
        #server_furnace에서 state를 갱신할 때까지 기다리기 위함
        t.sleep(2)

        lock.acquire()
        temp = datas.state_furnace()
        lock.release()

        #send나 recv가 lock 내부에 있으면 안된다.
        sock.sendall(temp.encode())

        num_opt = sock.recv(1024)
        number, option = num_opt.decode().split()
        #print(number + " " + option)

        #지정한 열처리로와 옵션이 가능한 옵션인지를 확인 (예] 켜져있지 않은 열처리로에 start옵션을 준 경우)
        lock.acquire()
        check, answer = datas.check_furnace(int(number), option)
        lock.release()

        sock.sendall(answer.encode())
        if not check:
            continue

        if option == 'end':
            q_msg = [number, option]
            lock.acquire()
            q.append(q_msg)
            lock.release()
        elif option == 'start':
            recv_pkt = sock.recv(1024)
            elem, manu, amount = read_packet(recv_pkt)

            sql = 'select temperature, time, gas from process where material = %s AND amount = %s AND manufacture = %s'
            val = (elem, amount, manu)
            dbcur.execute(sql, val)
            result = list(dbcur.fetchall())
            if  len(result) < 10:
                temper, time, gas = 100, 100, 'base_gas'
                send_pkt = packet_detail_set_process(temper, time, gas)
                sock.sendall(send_pkt)

            else:
                #지금은 똑같은 코드지만, 이후 추가될 내용으로는
                #데이터베이스로부터 얻은 데이터를 이용해 온도/시간/가스를 계산하도록 할 예정
                temper, time, gas = 70, 70, 'cal_gas'
                send_pkt = packet_detail_set_process(temper, time, gas)
                sock.sendall(send_pkt)

            recv_pkt = sock.recv(1024)
            temper, time, gas = read_packet(recv_pkt)

            #공정 시작 -> 공정식별번호 생성
            now = datetime.datetime.now()
            month = '{:02d}'.format(now.month)
            day = '{:02d}'.format(now.day)
            hour = '{:02d}'.format(now.hour)
            minute = '{:02d}'.format(now.minute)
            process_id = '{:02d}'.format(int(number)) + '_' + str(now.year)[-2:] + month + day + hour + minute

            msg = [number, option, process_id, elem, manu, amount, temper, time, gas]

            lock.acquire()
            q.append(msg)
            lock.release()

        elif option == 'fix':
            recv_pkt = sock.recv(1024)
            temper, time = read_packet(recv_pkt)

            msg = [str(number), option, temper, time]

            lock.acquire()
            q.append(msg)
            lock.release()
    sock.close()


##시작할 때 데이터베이스 읽어와서 실행중인 열처리로에 대해서는 order_list를 채워넣어야 한다.
def server_client2(sock:socket.socket, datas:Datas, q:list, dbconn, lock):
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
                temp = temp[:-1]
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
                temp = temp[:-1]
                sock.sendall(parameter.success_str.encode())
            else:
                sock.sendall((parameter.error_str + '_detail_fix').encode())
        elif recv_msg_list[0] == 'stop':
            temp.clear()
            sock.sendall(parameter.success_str.encode())
        else:
            sock.sendall((parameter.error_str + '_wrong msg type' + recv_msg_list[0]).encode())
    sock.close()

def server_simple(sock:socket.socket(), dbconn):
    #아직 while문 없다
    dbcur = dbconn.cursor()
    #sql = """select id from process where output is null"""   # <- 실제 상황때는 이걸 써야 한다. (작동중인 공정만 출력하도록!), 밑에는  데이터가 부족해 모든 프로세스를 읽어오도록 했다
    sql = """select id from process"""
    dbcur.execute(sql)
    result = dbcur.fetchall()
    processes = []              #parameter.total_furnace크기의 list, 각 index당 해당되는 열처리로의 진행중 공정을 나타낸다.
    last = []                   #parameter.total_furnace크기의 list, 각 index당 해당되는 열처리로의 가장 최근의 시각 (db의 current)를 나타낸다.
    sensors = []                #parameter.total_furnace크기의 list, 각 index당 해당되는 열처리로의 가장 최근의 센서값을 가지고 있다.

    for i in range(parameter.total_furnace):
        processes.append(None)
        last.append(None)
        sensors.append(None)

    for process in result:
        number = int(process[0][:2])
        processes[number - 1] = process[0]

    for process in processes:
        if process is None:
            sock.sendall(b'not working')
            sock.recv(1024)
            continue

        temp = ""
        number = int(process[:2])
        sql = """select * from furnace""" + str(number) +  """ where id = '""" + process + """' order by current desc limit 30"""
        dbcur.execute(sql)
        result = list(dbcur.fetchall())

        if len(result) == 0:
            sock.sendall(b'not yet')
            sock.recv(1024)
            continue

        result.reverse()

        #해당 프로세스의 가장 최근 센서 데이터
        sensors[number - 1] = result[-1]

        #해당 프로세스의 가장 최근 current
        last_current = result[-1][0]
        last[number-1] = last_current

        for step in result:
            for one_sensor in step:
                temp +=  str(one_sensor)
                temp += ' '
            temp += "/"
        #센서값 최대 30개 전송 -> 받을 때 recv 인자를 2048로
        sock.sendall(temp.encode())
        #동기화 목적
        sock.recv(1024)


    ##여기부터 이제 실시간으로 센서값 전송
    #print(last)
    
    while True:
        #simple client에게 보낼 str
        sensor_msg = ""

        dbconn.commit()
        #sql = """select id from process where output is null"""
        sql = """select id from process"""
        dbcur.execute(sql)
        result = dbcur.fetchall()

        #프로세스 식별자 초기화
        for i in range(parameter.total_furnace):
            processes[i] = None

        #작동중인 프로세스 조회
        for process in result:
            number = int(process[0][:2])
            processes[number - 1] = process[0]

        #작동중인 프로세스에서 센서값 조회
        for i in range(parameter.total_furnace):
            if processes[i] is None:
                last[i] = None
                sensors[i] = None
            else:
                number = int(processes[i][:2])
                sql = """select * from furnace""" + str(number) +  """ where id = '""" + processes[i] + """' order by current desc limit 1"""
                dbcur.execute(sql)
                result = list(dbcur.fetchall())
                
                #공정이 이제 막 시작되어 아직 센서값이 하나도 없는 경우
                if len(result) == 0:
                    continue

                last_current = result[0][0]
                #가장 최근 current가 직전에 보낸 센서데이터의 current와 동일하다면, 같은 데이터를 보내는 상황이므로 이를 무시하기 위함
                '''
                if last_current == last[i]:
                    continue
                '''

                #아닌 경우 last와 센서값 갱신
                last[i] = last_current
                sensors[i] = result[0]


        for sensor in sensors:
            if sensor is None:
                sensor_msg += 'None'
            else:
                for one_sensor in sensor:
                    sensor_msg += str(one_sensor)
                    sensor_msg += ' '
            sensor_msg += '/'
        
        sock.sendall(sensor_msg.encode())
        t.sleep(parameter.time_interval)

    
    sock.close()
    dbconn.close()

def in_client_use():
    s = Simple(parameter.host, parameter.port)
    s.connect()
    s.simple_first_recv()
    #s.confirm_data()
    while True:
        s.simple_recv_sensors()
    s.close()


#dash앱에서 사용할 thread
def monitoring(values, times, lock:threading.Lock):
    now_working_process = ['-', '-', '-', '-', '-', '-', '-', '-']
    dbconn = pymysql.connect(host=parameter.host, user=parameter.user, password=parameter.password, database=parameter.db, charset=parameter.charset)
    dbcur = dbconn.cursor()

    sql = """select id from process where output is null"""
    #sql = """select id from process"""
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
        times[int(number) - 1] = [get_time(one_step[0]) for one_step in sensors]
        lock.release()

    while True:
        dbconn.commit()
        sql = """select id from process where output is null"""
        #sql = """select id from process"""
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
            if len(times[index]) != 0  and times[index][-1] == get_time(sensors[0][0]):
                t.sleep(1)
                continue

            lock.acquire()
            if len(values[index]) >= 10:
                values[index][:-1] = values[index][1:]
                times[index][:-1] = times[index][1:]
                values[index][-1] = sensors[0][2:]
                times[index][-1] = get_time(sensors[0][0])
            else:
                values[index].append(sensors[0][2:])
                times[index].append(get_time(sensors[0][0]))
            lock.release()

        t.sleep(parameter.time_interval)

    dbconn.close()


#thread로 분리해서 실행할 함수는 아니지만, dash가 사용하는 thread에서만 사용하기에 이쪽에다 선언
def get_time(current):
    current = int(current)
    temp = (current // 10000) * 3600
    temp += (current % 10000) // 100 * 60
    temp += (current % 100)
    return temp

