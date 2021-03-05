import parameter
import furnace_content
import sys
import client
import button
import pymysql
import threading
import time
import json
from setting_content import SettingContent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap


class Select(QWidget):
    def __init__(self, stk_w, sock):
        super().__init__()
        self.stk_w = stk_w
        self.sock = sock
        self.initUI()
    
    def initUI(self):
        self.layout = QHBoxLayout()
        #image area
        self.image_area = QLabel()
        self.image_area.setPixmap(QPixmap(".\\images\\furnaces.png"))
        

        #furnace area, where furnace button placed
        self.furnace_area = QGridLayout()
        furnace_buttons = []
        for i in range(parameter.total_furnace): 
            furnace_buttons.append(QPushButton('furnace' + str(i + 1)))
            furnace_buttons[i].resize((parameter.height-100)//4, (parameter.height-100)//4)
            furnace_buttons[i].setMaximumHeight((parameter.height-100)//4)
            furnace_buttons[i].clicked.connect(lambda checked, index=i:self.furnace_button_click(index+1))
            self.furnace_area.addWidget(furnace_buttons[i], i // 2, i % 2)  

        #except setting area, which content is plot or furnace select
        self.layout.addWidget(self.image_area)
        self.layout.addLayout(self.furnace_area)
        self.setLayout(self.layout)

    def furnace_button_click(self, number:int):
        self.stk_w.setCurrentIndex(number)
        send_msg = 'num ' + str(number)
        self.sock.sendall(send_msg.encode())

        recv_msg = self.sock.recv(1024).decode()
        #print(recv_msg)

    

class HomePage(QWidget):
    def __init__(self, sock, dbconn):
        super().__init__()
        self.sock = sock
        self.dbconn = dbconn

        #load combobox content from json file test
        with open(parameter.json_path, 'r') as combo_json:
            self.combo_opt = json.load(combo_json)

        self.initUI()


    def initUI(self):
        self.setStyleSheet('background-color:white')
        self.layout = QHBoxLayout()
        self.dyn_content = QStackedWidget()

        #setting area, where setting button, back button and icon image placed
        self.setting_area = QVBoxLayout()
        
        icon = QLabel()
        icon.setPixmap(QPixmap('.\\images\\logo.png'))


        empty = QWidget()

        set_button = QPushButton('setting')
        set_button.clicked.connect(lambda:button.set_button_click(self.dyn_content))
        back_button = QPushButton('back')
        back_button.clicked.connect(self.back_button_click)

        self.setting_area.addWidget(icon, 1)
        self.setting_area.addWidget(empty, 7)
        self.setting_area.addWidget(set_button, 1)
        self.setting_area.addWidget(back_button, 1)

        #changeable area
        self.content_area = Select(self.dyn_content, self.sock)
        self.dyn_content.addWidget(self.content_area)
        self.furnace_list = []
        for i in range(parameter.total_furnace):
            self.furnace_list.append(furnace_content.FurnaceContent(i+1, self.sock, self.dbconn, self.combo_opt))
            self.dyn_content.addWidget(self.furnace_list[i])
        
        self.dyn_content.addWidget(SettingContent(self.combo_opt))

        t = threading.Thread(target=monitoring, args=(self.dbconn, self.furnace_list))
        t.daemon = True
        t.start()

        #settting area | image area | furnace area
        self.layout.addLayout(self.setting_area, 1)
        self.layout.addWidget(self.dyn_content, 10)

        self.setLayout(self.layout)
        self.setWindowTitle('CPS ProtoType')
        self.setGeometry(0, 0, parameter.width, parameter.height)
    
    def back_button_click(self):
        self.dyn_content.setCurrentIndex(0)
        self.sock.sendall('esc'.encode())

        recv_msg = self.sock.recv(1024).decode()
        #print(recv_msg)

    def set_button_click(self):
        self.dyn_content.setCurrentIndex(parameter.total_furnace + 1)


def monitoring(dbconn, furnace_pages):
    dbconn.commit()
    dbcur = dbconn.cursor()
    now_working_process = ['-', '-', '-', '-', '-', '-', '-', '-']

    #sql = parameter.sql
    sql = parameter.test_sql
    dbcur.execute(sql)
    processes = dbcur.fetchall()   

    for process in processes:
        number = int(process[0][:2])

        if now_working_process[number - 1] == '-':
            now_working_process[number - 1] = process[0]
        else:
            if int(now_working_process[number - 1].split('_')[-1]) <= int(process[0].split('_')[-1]):
                now_working_process[number - 1] = process[0]
        
        sql = """select * from furnace""" + str(number) +  """ where id = '""" + process[0] + """' order by current desc limit 50"""
        dbcur.execute(sql)
        sensors = list(dbcur.fetchall())
        sensors.reverse()
        for sensor in sensors:
            sensor = list(sensor)
        #furnace_pages[number - 1].sensor_area.init_data(sensors) #test area 영역 대신 원래 사용되던 코드

        
        sql = """select * from process where id = '""" + process[0] + """'"""
        dbcur.execute(sql)
        processes = list(dbcur.fetchall()[0]) 
        furnace_pages[number - 1].init_data(processes, sensors)
        

    while True:
        dbconn.commit()
        #sql = parameter.sql
        sql = parameter.test_sql
        dbcur.execute(sql)
        processes = dbcur.fetchall()


        for process in processes:
            number = int(process[0][:2])
            if now_working_process[number - 1] == '-':
                now_working_process[number - 1] = process[0] 

            if now_working_process[number - 1] not in processes:
                now_working_process[number - 1] = '-'
                #초기화 함수 필요할듯   

            sql = """select * from furnace""" + str(number) +  """ where id = '""" + process[0] + """' order by current desc limit 1"""
            dbcur.execute(sql)
            sensors = list(dbcur.fetchall())

            if len(sensors) == 0:
                continue
            
            sensors = list(sensors[0])
            furnace_pages[number - 1].sensor_area.update(sensors)
        time.sleep(parameter.time_interval)
    dbcur.close()


if __name__ == "__main__":
    #C = client.Client(parameter.host, parameter.port)
    #C.connect()

    app = QApplication(sys.argv)
    form = HomePage()
    form.show()

    sys.exit(app.exec_())