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

    크게 2 부분으로 나뉜다.
    
    """
    dbcur = dbconn.cursor()
    process_id = ''
    is_running = False
    end_flag = False
    index = number - 1
    time_interval = parameter.time_interval

    str_number = '{:02d}'.format(int(number))
    #print(str_number)
    sql = f"""UPDATE process SET output = 3 where output is Null and id like '{str_number}%'"""
    dbcur.execute(sql)
    dbconn.commit()

    while True: #add while
        #wait until recv process operation order
        while datas.datas[index]['state'] == 'on':
            for elem in q:
                if elem[1] == 'start':
                    #lock.acquire()
                    process_id, mete, manu, inp, count, temp_list, heattime_list, staytime_list, gas = utils.extract_detail_option(elem)

                    if not check_process(dbcur, process_id):
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

                    #lock.acquire()
                    datas.working_furnace_data(number, process_id) 

                    q.remove(elem)
                    #lock.release()
                    break
                else:
                    #lock.acquire()
                    print('[server] ignore msg in q : ' + str(elem[0]) + " : " + elem[1])
                    q.remove(elem)
                    #lock.release()
            t.sleep(time_interval)

        #after furnace starts process
        while True:
            no_signal = True
            end_flag = False
            #lock.acquire()
            for elem in q:
                if elem[1] == 'end':
                    end_flag = True
                    sock.sendall(b'end signal')
                    no_signal = False
                    lock.acquire()
                    q.clear()
                    lock.release()
                    break
                elif elem[1] == 'fix': #이 부분 수정필요
                    sock.sendall(b'fix signal')
                    test = sock.recv(1024) #recv fix confirm msg from furnace
                    print(f'testline in thread 91, {test.decode()}')
                    process_id, mete, manu, inp, count, temp_list, heattime_list, staytime_list, gas = utils.extract_detail_option(elem)

                    send_pkt = packet_detail_setting(count, elem[7:7+count], elem[7 + count : 7 + (2 * count)], elem[7 + (2 * count) : 7 + (3 * count)], gas)
                    sock.sendall(send_pkt)

                    #데이터베이스에 공정정보를 수정한 값으로 갱신
                    sql = "UPDATE process SET material = %s, amount = %s, manufacture = %s, count = %s, temper1 = %s, temper2 = %s, temper3 = %s, temper4 = %s, temper5 = %s, temper6 = %s, temper7 = %s, temper8 = %s, temper9 = %s, temper10 = %s, heattime1 = %s, heattime2 = %s, heattime3 = %s, heattime4 = %s, heattime5 = %s, heattime6 = %s, heattime7 = %s, heattime8 = %s, heattime9 = %s, heattime10 = %s, staytime1 = %s, staytime2 = %s, staytime3 = %s, staytime4 = %s, staytime5 = %s, staytime6 = %s, staytime7 = %s, staytime8 = %s, staytime9 = %s, staytime10 = %s, gas = %s WHERE id = %s"
                    val = (mete, int(inp), manu, count, temp_list[0], temp_list[1], temp_list[2], temp_list[3], temp_list[4], temp_list[5], temp_list[6], temp_list[7], temp_list[8], temp_list[9], heattime_list[0], heattime_list[1], heattime_list[2], heattime_list[3], heattime_list[4], heattime_list[5], heattime_list[6], heattime_list[7], heattime_list[8], heattime_list[9], staytime_list[0], staytime_list[1], staytime_list[2], staytime_list[3], staytime_list[4], staytime_list[5], staytime_list[6], staytime_list[7], staytime_list[8], staytime_list[9], gas, process_id)

                    dbcur.execute(sql, val)
                    dbconn.commit()
                    
                    no_signal = False   #이거 if 문 밖에서 안으로 이동
                #lock.acquire()
                q.remove(elem)
                #lock.release()
            #lock.release()

            if no_signal:
                sock.sendall(b'no_signal')

            #abnormal end of process
            if end_flag:
                sql = "UPDATE process SET output = %s WHERE id = %s"
                val = (int(1), process_id)
                dbcur.execute(sql, val)
                dbconn.commit()

                #lock.acquire()    
                datas.on_furnace_data(number)
                #lock.release()
                break
            
            #recv sensor value from furnace
            pkt = sock.recv(1024)
    
            touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press, last = read_packet(pkt)

            #create current value which represent current time
            current_time = utils.make_current()

            #save sensor value to database
            sql = """INSERT INTO furnace%s(current, id, touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            val = (number, current_time, process_id, touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press)
            dbcur.execute(sql, val)
            dbconn.commit()

            #normal end of process
            if last == 'True':
                #sock.sendall(b'end signal')    #<-이거 꼭 필요한건가, 이거 furnace 자체에서 공정종료를 먼저 하기 때문에 굳이 보낼 필요 없을듯
                sql = "UPDATE process SET output = %s WHERE id = %s"
                val = (int(0), process_id)
                dbcur.execute(sql, val)
                dbconn.commit()

                #lock.acquire()   
                datas.on_furnace_data(number)
                #lock.release()
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

            lock.acquire()
            state = datas.datas[number - 1]['state']
            process = datas.datas[number - 1]['process']
            lock.release()

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

            lock.acquire()
            q[number - 1].append(q_msg)
            lock.release()

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

            lock.acquire()
            q[number - 1].append(q_msg)
            lock.release()

            sock.sendall(parameter.success_str.encode())
        elif recv_msg_list[0] == 'end': #when end process button is clicked
            temp.clear()
            q_msg = [str(number), recv_msg_list[0]]

            lock.acquire()
            q[number - 1].append(q_msg)
            lock.release()

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
