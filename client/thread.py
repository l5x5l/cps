import sys
import time
import subprocess
import utils
import parameter
import output_receiver

from PyQt5.QtCore import QThread, pyqtSignal

class Monitoring(QThread):
    update_sensor = pyqtSignal(int, list)       #그래프 업데이트 할 때 발생
    nature_end = pyqtSignal(int)                #공정이 정상 종료될 때 발생 (버튼을 누르거나 중간에 예상치 못하게 종료된 거 말고)
    clear_signal = pyqtSignal(int)              #그래프를 초기화할 때 발생

    def __init__(self, dbconn, working_process = []):
        QThread.__init__(self)
        self.dbconn = dbconn
        self.dbcur = dbconn.cursor()
        self.now_working_process = working_process
        
    def __del__(self):
        self.dbconn.close()
        self.wait()

    def run(self):
        while True:
            checkpoint = time.time()
            self.dbconn.commit()
            processes = utils.get_working_process(self.dbcur)
            for i in range(len(processes)):
                if processes[i] == '-':     
                    if self.now_working_process[i] == '-':   # 공정이 존재하지 않은 경우
                        continue        
                    else:          #공정이 종료된 경우
                        self.dbconn.commit()                      
                        sql = f"""select output from process where id = '{self.now_working_process[i]}'"""
                        self.dbcur.execute(sql)
                        result = self.dbcur.fetchall()
                        self.now_working_process[i] = processes[i]   
                        if result[0][0] == 0:
                            self.nature_end.emit(i)
                
                if self.now_working_process[i] == '-' and processes[i] != '-':   # 공정이 새로 시작된 경우
                    self.clear_signal.emit(i)
                    self.now_working_process[i] = processes[i]

                sql = """select * from furnace""" + str(i+1) +  """ where id = '""" + self.now_working_process[i] + """' order by current desc limit 1"""
                self.dbcur.execute(sql)
                sensors = list(self.dbcur.fetchall())
                if len(sensors) == 0:
                    continue
                
                sensors = list(sensors[0])
                self.update_sensor.emit(i, sensors)

            if (time.time() - checkpoint) > parameter.time_interval:                #while문 내의 코드 실행이 2초 이상 지난 경우
                utils.sleep(parameter.time_interval)
            else:
                utils.sleep(parameter.time_interval - (time.time() - checkpoint))    #정확히 2초의 간격을 유지하기 위함
        

class EndprocessSurvey(QThread):
    def __init__(self, output_receiver):
        QThread.__init__(self)
        self.output_receiver = output_receiver

    def run(self):
        while True:
            process_option_str = self.output_receiver.recv_msg()
            self.output_receiver.send_msg('confirm msg')

            if process_option_str == "empty":
                continue
            else:
                print(f"testcase {process_option_str}")
                subprocess.call([sys.executable, '.\\outputReceiver_main.py', process_option_str])

    def __del__(self):
        self.wait()
