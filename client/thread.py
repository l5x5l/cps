import sys
import time
import subprocess
import utils
import parameter
import output_receiver

def monitoring(dbconn, furnace_pages, working_process = []):
    """
    get realtime sensor data from database
    dbconn(database connector)
    furnace_pages(list) : list of furnace_content instance
    working_process(list) : list of exist working process's id
    ex ['01_00000000', '-', '-', '-', '05_00000000', '-', '-', '-']
    """
    dbcur = dbconn.cursor()
    now_working_process = working_process

    # 프로그램 실행 후, 진행중인 공정에 대한 센서값 업데이트
    while True:
        checkpoint = time.time()    
        dbconn.commit()
        processes = utils.get_working_process(dbcur)
        for i in range(len(processes)):
            if processes[i] == '-':     
                if now_working_process[i] == '-':   # 공정이 존재하지 않은 경우
                    continue        
                else:          #공정이 종료된 경우
                    dbconn.commit()                      
                    sql = f"""select output from process where id = '{now_working_process[i]}'"""
                    dbcur.execute(sql)
                    result = dbcur.fetchall()
                    now_working_process[i] = processes[i]   
                    if result[0][0] == 0:
                        furnace_pages[i].stop_process_nature()


            if now_working_process[i] == '-' and processes[i] != '-':   # 공정이 새로 시작된 경우
                furnace_pages[i].sensor_area.clear()
                now_working_process[i] = processes[i]

            sql = """select * from furnace""" + str(i+1) +  """ where id = '""" + now_working_process[i] + """' order by current desc limit 1"""
            dbcur.execute(sql)
            sensors = list(dbcur.fetchall())

            if len(sensors) == 0:
                continue
            
            sensors = list(sensors[0])
            furnace_pages[i].signal(sensors)

        if (time.time() - checkpoint) > parameter.time_interval:                #while문 내의 코드 실행이 2초 이상 지난 경우
            utils.sleep(parameter.time_interval)
            #time.sleep(parameter.time_interval)
        else:
            utils.sleep(parameter.time_interval - (time.time() - checkpoint))
            #time.sleep(parameter.time_interval - (time.time() - checkpoint))    #정확히 2초의 간격을 유지하기 위함
        
    dbcur.close()

def endprocess_survey(output_receiver:output_receiver.OutputReceiver):
    """
    server의 server_outputReceiver thread와 대응
    정상 종료된 공정에 대한 정보를 받은 후 해당 정보를 exec의 인자로 전달

    output_receiver : OutputReceiver instance
    """

    while True:
        process_option_str = output_receiver.recv_msg()
        output_receiver.send_msg('confirm msg')

        if process_option_str == "empty":
            continue
        else:
            print(f"testcase {process_option_str}")
            subprocess.call([sys.executable, '.\\outputReceiver_main.py', process_option_str])