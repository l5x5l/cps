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
    dbcur = dbconn.cursor()
    process_id = '-'
    is_running = False
    index = number - 1
    time_interval = parameter.time_interval

    q.clear()   #remove order before furnace turn on

    while True: 
        #wait until recv process operation order
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

                lock.acquire()
                datas.working_furnace_data(number, process_id) 
                lock.release()
            elif elem[1] == 'end':
                sock.sendall(b'end signal')
                process_id = '-'

                sql = "UPDATE process SET output = %s WHERE id = %s"
                val = (int(1), process_id)
                dbcur.execute(sql, val)
                dbconn.commit()

                lock.acquire()
                q.clear()
                datas.on_furnace_data(number)
                lock.release()
                
            elif elem[1] == 'fix':
                sock.sendall(b'fix signal')
                process_id, mete, manu, inp, count, temp_list, heattime_list, staytime_list, gas = utils.extract_detail_option(elem)

                send_pkt = packet_detail_setting(count, elem[7:7+count], elem[7 + count : 7 + (2 * count)], elem[7 + (2 * count) : 7 + (3 * count)], gas)
                sock.sendall(send_pkt)
                sock.recv(1024)

                sql = "UPDATE process SET material = %s, amount = %s, manufacture = %s, count = %s, temper1 = %s, temper2 = %s, temper3 = %s, temper4 = %s, temper5 = %s, temper6 = %s, temper7 = %s, temper8 = %s, temper9 = %s, temper10 = %s, heattime1 = %s, heattime2 = %s, heattime3 = %s, heattime4 = %s, heattime5 = %s, heattime6 = %s, heattime7 = %s, heattime8 = %s, heattime9 = %s, heattime10 = %s, staytime1 = %s, staytime2 = %s, staytime3 = %s, staytime4 = %s, staytime5 = %s, staytime6 = %s, staytime7 = %s, staytime8 = %s, staytime9 = %s, staytime10 = %s, gas = %s WHERE id = %s"
                val = (mete, int(inp), manu, count, temp_list[0], temp_list[1], temp_list[2], temp_list[3], temp_list[4], temp_list[5], temp_list[6], temp_list[7], temp_list[8], temp_list[9], heattime_list[0], heattime_list[1], heattime_list[2], heattime_list[3], heattime_list[4], heattime_list[5], heattime_list[6], heattime_list[7], heattime_list[8], heattime_list[9], staytime_list[0], staytime_list[1], staytime_list[2], staytime_list[3], staytime_list[4], staytime_list[5], staytime_list[6], staytime_list[7], staytime_list[8], staytime_list[9], gas, process_id)

                dbcur.execute(sql, val)
                dbconn.commit()
                
            lock.acquire()
            q.remove(elem)
            lock.release()



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
        lock.acquire()
        data = datas.state_furnace()
        print(datas.datas[0]['process'])
        lock.release()

        recv_msg = sock.recv(1024).decode()
        recv_msg_list = recv_msg.split()
        if recv_msg_list[0] == 'esc':   #when back button is clicked
            temp = None
            number = None
            sock.sendall(parameter.success_str.encode())
        elif recv_msg_list[0] == 'num':     #when furnace button is clicked
            #[message example] num 1 -> select furnace1
            if temp is None:
                number = int(recv_msg_list[1])
                temp = order_list[number - 1]
                sock.sendall(parameter.success_str.encode())
            else:
                sock.sendall((parameter.error_str + '_num').encode())
        elif recv_msg_list[0] == 'base':    #when base setting button is clicked
            if temp is not None and len(temp) == 0:
                base_element = recv_msg_list[1:]
                temp.append(base_element)
                sock.sendall(parameter.success_str.encode())
            else:
                sock.sendall((parameter.error_str + '_base').encode())
        elif recv_msg_list[0] == 'base_fix':    #when base modify button is clicked
            if temp is not None and len(temp) == 1:
                prev_base = temp[-1]
                temp.pop()
                sock.sendall(parameter.success_str.encode())
            else:
                sock.sendall((parameter.error_str + '_base_fix').encode())
        elif recv_msg_list[0] == 'detail':  #when datail setting button is clicked
            if temp is not None and len(temp) == 1:
                detail_element = recv_msg_list[1:]
                temp.append(detail_element)

                #공정식별번호 생성
                process_id = utils.make_process_id(number)

                q_msg = [str(number), 'start', process_id] + temp[0] + temp[1]

                lock.acquire()
                q[number - 1].append(q_msg)
                lock.release()

                sock.sendall(parameter.success_str.encode())
            else:
                sock.sendall((parameter.error_str + '_detail').encode())
        elif recv_msg_list[0] == 'detail_fix':  #when detail modify button is clicked
            if temp is not None and len(temp) == 2:
                prev_detail = temp[-1]
                temp.pop()
                sock.sendall(parameter.success_str.encode())
            else:
                sock.sendall((parameter.error_str + '_detail_fix').encode())
        #아직 구현 안됨
        elif recv_msg_list[0] == 'modify_process':    #when after detail setting is changed, datail button is clicked (send modified detail setting about exists process)
            if temp is not None and len(temp) == 1:
                detail_element = recv_msg_list[1:]
                temp.append(detail_element)
                #이제 q에 입력해야 한다.
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
