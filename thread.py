import parameter
import socket
import threading
import pymysql
import datetime
import utils
from packet import *
from data import Datas
import time as t

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


def server_furnace(sock:socket.socket, number:int, datas:Datas, q:list, dbconn, lock):
    """
    server's thread which connected with furnace
    socket(socket.socket) : 열처리로와 연결한 socket
    number(int) : 열처리로의 번호
    datas(Datas class) : 열처리로의 상태, 해당 열처리로가 진행하고 있는 공정에 대한 정보를 담고 있는 instance
    dbconn(database connector) : 데이터베이스에 센서값을 저장하는데 사용
    lock(threading.lock) : critical section 방지용


    큰 구조는 아래와 같다
    while:
        공정시작신호를 받을 때까지 while:
            ~~~~~~
        공정이 종료될 때까지 while:
            ~~~~~~
    """
    dbcur = dbconn.cursor()
    process_id = ''
    is_running = False
    end_flag = False
    index = number - 1
    time_interval = parameter.time_interval

    str_number = '{:02d}'.format(int(number))
    sql = f"""UPDATE process SET output = 3 where output is Null and id like '{str_number}%'"""
    dbcur.execute(sql)
    dbconn.commit()

    while True: #add while
        while datas.datas[index]['state'] == 'on':  #서버와 연결된 상태라면(on) 공정시작신호가 올 때까지 대기
            for elem in q:
                if elem[1] == 'start':  #공정시작신호를 받은 경우
                    process_id, mete, manu, inp, count, temp_list, heattime_list, staytime_list, gas = utils.extract_detail_option(elem)

                    if not check_process(dbcur, process_id):    #만에하나 현 공정과 동일한 id를 가진 공정이 감지된 경우, 그 공정에 대한 정보를 삭제하고 현 공정으로 덮어씀
                        sql = "UPDATE process SET material = %s, amount = %s, manufacture = %s, count = %s, temper1 = %s, temper2 = %s, temper3 = %s, temper4 = %s, temper5 = %s, temper6 = %s, temper7 = %s, temper8 = %s, temper9 = %s, temper10 = %s, heattime1 = %s, heattime2 = %s, heattime3 = %s, heattime4 = %s, heattime5 = %s, heattime6 = %s, heattime7 = %s, heattime8 = %s, heattime9 = %s, heattime10 = %s, staytime1 = %s, staytime2 = %s, staytime3 = %s, staytime4 = %s, staytime5 = %s, staytime6 = %s, staytime7 = %s, staytime8 = %s, staytime9 = %s, staytime10 = %s, gas = %s, output = %s WHERE id = %s"
                        val = (mete, int(inp), manu, count, temp_list[0], temp_list[1], temp_list[2], temp_list[3], temp_list[4], temp_list[5], temp_list[6], temp_list[7], temp_list[8], temp_list[9], heattime_list[0], heattime_list[1], heattime_list[2], heattime_list[3], heattime_list[4], heattime_list[5], heattime_list[6], heattime_list[7], heattime_list[8], heattime_list[9], staytime_list[0], staytime_list[1], staytime_list[2], staytime_list[3], staytime_list[4], staytime_list[5], staytime_list[6], staytime_list[7], staytime_list[8], staytime_list[9], gas, None, process_id)
                        dbcur.execute(sql, val)
                        dbconn.commit()

                        sql = f"""DELETE from furnace{number} WHERE id = '{process_id}'"""
                        dbcur.execute(sql)
                        dbconn.commit()
                        
                    else:
                        sql = "INSERT INTO process(id, material, amount, manufacture, count, temper1, temper2, temper3, temper4, temper5, temper6, temper7, temper8, temper9, temper10, heattime1, heattime2, heattime3, heattime4, heattime5, heattime6, heattime7, heattime8, heattime9, heattime10, staytime1, staytime2, staytime3, staytime4, staytime5, staytime6, staytime7, staytime8, staytime9, staytime10,gas) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        val = (process_id, mete, int(inp), manu, count, temp_list[0], temp_list[1], temp_list[2], temp_list[3], temp_list[4], temp_list[5], temp_list[6], temp_list[7], temp_list[8], temp_list[9], heattime_list[0], heattime_list[1], heattime_list[2], heattime_list[3], heattime_list[4], heattime_list[5], heattime_list[6], heattime_list[7], heattime_list[8], heattime_list[9], staytime_list[0], staytime_list[1], staytime_list[2], staytime_list[3], staytime_list[4], staytime_list[5], staytime_list[6], staytime_list[7], staytime_list[8], staytime_list[9], gas)
                        dbcur.execute(sql, val)
                        dbconn.commit()

                    send_pkt = packet_detail_setting(count, elem[7:7+count], elem[7 + count : 7 + (2 * count)], elem[7 + (2 * count) : 7 + (3 * count)], gas)
                    sock.sendall(send_pkt)

                    lock.acquire()
                    datas.working_furnace_data(number, process_id) 
                    q.remove(elem)
                    lock.release()
                    break
                else:   #공정시작 전 공정수정/공정중지 신호가 온 경우 이를 무시하기 위해 존재
                    print('[server] ignore msg in q : ' + str(elem[0]) + " : " + elem[1])
                    lock.acquire()
                    q.remove(elem)
                    lock.release()
            t.sleep(time_interval)

        #after furnace starts process
        while True:
            no_signal = True
            end_flag = False
            for elem in q:
                if elem[1] == 'end':
                    end_flag = True
                    sock.sendall(b'end signal')
                    no_signal = False
                    lock.acquire()
                    q.clear()
                    lock.release()
                    break
                elif elem[1] == 'fix':
                    sock.sendall(b'fix signal')
                    _ = sock.recv(1024) #열처리로가 recv하기 전 바로 뒤에 sendall이 보낸 메세지와 fix signal이 합쳐지지 않게 하기 위해 
                    process_id, mete, manu, inp, count, temp_list, heattime_list, staytime_list, gas = utils.extract_detail_option(elem)

                    send_pkt = packet_detail_setting(count, elem[7:7+count], elem[7 + count : 7 + (2 * count)], elem[7 + (2 * count) : 7 + (3 * count)], gas)
                    sock.sendall(send_pkt)

                    #데이터베이스에 존재하는 공정정보를 수정한 값으로 갱신
                    sql = "UPDATE process SET material = %s, amount = %s, manufacture = %s, count = %s, temper1 = %s, temper2 = %s, temper3 = %s, temper4 = %s, temper5 = %s, temper6 = %s, temper7 = %s, temper8 = %s, temper9 = %s, temper10 = %s, heattime1 = %s, heattime2 = %s, heattime3 = %s, heattime4 = %s, heattime5 = %s, heattime6 = %s, heattime7 = %s, heattime8 = %s, heattime9 = %s, heattime10 = %s, staytime1 = %s, staytime2 = %s, staytime3 = %s, staytime4 = %s, staytime5 = %s, staytime6 = %s, staytime7 = %s, staytime8 = %s, staytime9 = %s, staytime10 = %s, gas = %s WHERE id = %s"
                    val = (mete, int(inp), manu, count, temp_list[0], temp_list[1], temp_list[2], temp_list[3], temp_list[4], temp_list[5], temp_list[6], temp_list[7], temp_list[8], temp_list[9], heattime_list[0], heattime_list[1], heattime_list[2], heattime_list[3], heattime_list[4], heattime_list[5], heattime_list[6], heattime_list[7], heattime_list[8], heattime_list[9], staytime_list[0], staytime_list[1], staytime_list[2], staytime_list[3], staytime_list[4], staytime_list[5], staytime_list[6], staytime_list[7], staytime_list[8], staytime_list[9], gas, process_id)

                    dbcur.execute(sql, val)
                    dbconn.commit()
                    
                    no_signal = False
                lock.acquire()
                q.remove(elem)
                lock.release()

            if no_signal:
                sock.sendall(b'no_signal')  #어떠한 명령도 입력되지 않음을 열처리로에 전송

            #공정 중지버튼으로 인한 중단(비정상 종료)의 경우
            if end_flag:
                sql = "UPDATE process SET output = %s WHERE id = %s"
                val = (int(1), process_id)
                dbcur.execute(sql, val)
                dbconn.commit()

                lock.acquire()    
                datas.on_furnace_data(number)
                lock.release()
                break
            
            pkt = sock.recv(1024)   #센서값 수신
    
            touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press, last = read_packet(pkt)

            #create current value which represent current time
            current_time = utils.make_current()

            #센서값을 데이터베이스에 저장
            sql = """INSERT INTO furnace%s(current, id, touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            val = (number, current_time, process_id, touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press)
            dbcur.execute(sql, val)
            dbconn.commit()

            #모든 공정과정이 끝난 경우(정상종료)
            #중지신호를 열처리로에 전송하는 비정상종료와는 다르게, 열처리로 자체에서 종료 처리를 하므로 중지신호를 보낼 필요가 없다
            if last == 'True':
                sql = "UPDATE process SET output = %s WHERE id = %s"
                val = (int(0), process_id)
                dbcur.execute(sql, val)
                dbconn.commit()

                lock.acquire()   
                datas.on_furnace_data(number)
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
        recv_msg = sock.recv(1024).decode()
        recv_msg_list = recv_msg.split()

        if recv_msg_list[0] == 'esc':   #when back button is clicked
            temp = None
            number = None
            sock.sendall(parameter.success_str.encode())
        elif recv_msg_list[0] == 'num':     #when furnace button is clicked
            #[message example] num 1 -> select furnace1
            number = int(recv_msg_list[1])
            temp = order_list[number - 1]

            lock[number - 1].acquire()
            state = datas.datas[number - 1]['state']
            process = datas.datas[number - 1]['process']
            lock[number - 1].release()

            sock.sendall((state + ' ' + process).encode())
        elif recv_msg_list[0] == 'base':    #when base setting button is clicked
            temp.clear()
            base_element = recv_msg_list[1:]
            temp.append(base_element)
            sock.sendall(parameter.success_str.encode())
        elif recv_msg_list[0] == 'base_fix':    #when base modify button is clicked
            prev_base = temp[-1]
            temp.pop()
            sock.sendall(parameter.success_str.encode())
        elif recv_msg_list[0] == 'detail':  #when datail setting button is clicked
            detail_element = recv_msg_list[1:]
            temp.append(detail_element)

            #공정식별번호 생성
            process_id = utils.make_process_id(number)

            q_msg = [str(number), 'start', process_id] + temp[0] + temp[1]

            lock[number - 1].acquire()
            q[number - 1].append(q_msg)
            lock[number - 1].release()

            sock.sendall(parameter.success_str.encode())
        elif recv_msg_list[0] == 'detail_fix':  #when detail modify button is clicked
            #if temp is not None and len(temp) == 2:
            prev_detail = temp[-1]
            temp.pop()
            sock.sendall(parameter.success_str.encode())
        elif recv_msg_list[0] == 'restart':    #when after detail setting is changed, datail button is clicked (send modified detail setting about exists process)
            detail_element = recv_msg_list[1:]
            temp.append(detail_element)
 
            q_msg = [str(number), 'fix', process_id] + temp[0] + temp[1]

            lock[number - 1].acquire()
            q[number - 1].append(q_msg)
            lock[number - 1].release()

            sock.sendall(parameter.success_str.encode())
        elif recv_msg_list[0] == 'end': #when end process button is clicked
            temp.clear()
            q_msg = [str(number), recv_msg_list[0]]

            lock[number - 1].acquire()
            q[number - 1].append(q_msg)
            lock[number - 1].release()

            sock.sendall(parameter.success_str.encode())
        elif recv_msg_list[0] == 'init':
            process_id = recv_msg_list[1]
            number = int(recv_msg_list[2])
            base_element = recv_msg_list[3:6]
            detail_element = recv_msg_list[6:]
            temp = order_list[number - 1]
            temp.append(base_element)
            temp.append(detail_element)
            temp = None

            sock.sendall(parameter.success_str.encode())
        else:
            sock.sendall((parameter.error_str + '_wrong msg type' + recv_msg_list[0]).encode())
    sock.close()
