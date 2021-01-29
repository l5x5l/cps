import parameter
import socket
import threading
import pymysql
import datetime
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

    #연결한 열처리로가 작업을 시작할 때까지 대기후 작업을 시작하는 신호를 수신한 경우 공정 설정값 전송
    print(datas.datas[index]['state'])
    while datas.datas[index]['state'] == 'on':
        lock.acquire()
        for elem in q:
            if elem[0] == str(number):
                if elem[1] == 'start':
                    process_id, mete, manu, inp, temper, time, gas = elem[2:]
                    sql = "INSERT INTO process(id, material, amount, manufacture, temperature, time, gas) VALUES(%s, %s, %s, %s, %s, %s, %s)"
                    val = (process_id, mete, int(inp), manu, int(temper), int(time), gas)
                    dbcur.execute(sql, val)
                    dbconn.commit()

                    send_pkt = packet_detail_set_process(temper, time, gas)
                    sock.sendall(send_pkt)

                    datas.working_furnace_data(number, process_id)

                    q.remove(elem)
                    break
                else:
                    print('[server] ignore msg in q : ' + str(elem[0]) + " : " + elem[1])

                q.remove(elem)
        lock.release()
        t.sleep(time_interval)

    print(datas.datas[index]['state'])

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
                elif elem[1] == 'start':
                    sock.sendall(b'start signal')
                elif elem[1] == 'fix':
                    sock.sendall(b'fix signal')
                    temper, time = elem[2:]
                    send_pkt = packet_fix(temper, time)
                    #데이터베이스에 공정정보를 수정한 값으로 갱신
                    sql = "UPDATE process SET temperature = %s, time = %s WHERE id = %s"
                    val = (temper, time, process_id)
                    
                no_signal = False
                q.remove(elem)
        lock.release()

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
        temp = datas.state_furnace()
        sock.sendall(temp.encode())

        num_opt = sock.recv(1024)
        number, option = num_opt.decode().split()
        #print(number + " " + option)

        #지정한 열처리로와 옵션이 가능한 옵션인지를 확인 (예] 켜져있지 않은 열처리로에 start옵션을 준 경우)
        check, answer = datas.check_furnace(int(number), option)

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

                print(result)
                
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