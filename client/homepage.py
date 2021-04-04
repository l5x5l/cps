from settingPage import SettingPage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
import pymysql
import threading
import time
import json

import client
import output_receiver
import button
import parameter
import furnacePage
import utils
import thread

class FurnaceSelectArea(QWidget):
    """
    homePage에서 열처리로 선택하는 부분(우측)
    """
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
        

        # 열처리로 선택버튼을 열처리로의 개수만큼 생성
        self.furnace_area = QGridLayout()
        furnace_buttons = []
        for i in range(parameter.total_furnace): 
            furnace_buttons.append(QPushButton('furnace' + str(i + 1)))
            furnace_buttons[i].resize((parameter.height-100)//4, (parameter.height-100)//4)
            furnace_buttons[i].setMaximumHeight((parameter.height-100)//4)
            furnace_buttons[i].clicked.connect(lambda checked, index=i:self.furnace_button_click(index+1))
            self.furnace_area.addWidget(furnace_buttons[i], i // 2, i % 2)  

        # 메인 레이아웃에 결합
        self.layout.addWidget(self.image_area)
        self.layout.addLayout(self.furnace_area)
        self.setLayout(self.layout)

    def furnace_button_click(self, number:int):
        """
        열처리로 선택 버튼 클릭시 이벤트함수
        """
        self.stk_w.setCurrentIndex(number)
        send_msg = 'num ' + str(number)         #server에 몇 번 열처리로를 선택했는지 알리는 역할
        self.sock.sendall(send_msg.encode())

        recv_msg = self.sock.recv(1024).decode()
        recv_msg_list = recv_msg.split()
        state = recv_msg_list[0]
        process = None
        if len(recv_msg_list) != 1:
            process = recv_msg_list[1]

        self.stk_w.widget(number).SetStateText(state, process)

    
class HomePage(QWidget):
    def __init__(self, Client, OutputReceiver, dbconn):
        super().__init__()
        self.Client_instance = Client
        self.OutputReceiver_instance = OutputReceiver
        self.sock = Client.sock
        self.dbconn = dbconn

        # qcombobox에 들어갈 값들을 json파일로부터 읽어옴
        with open(parameter.json_path, 'r') as combo_json:
            self.combo_opt = json.load(combo_json)
        
        self.initUI()


    def initUI(self):
        self.setStyleSheet('background-color:white')
        self.mainlayout = QHBoxLayout()
        self.dyn_content = QStackedWidget()

        #setting area, where setting button, back button and icon image placed
        self.setting_area = QVBoxLayout()
        
        icon = QLabel()
        icon.setPixmap(QPixmap('.\\images\\logo.png'))


        empty = QWidget()

        set_button = QPushButton('setting')
        set_button.clicked.connect(self.set_button_click)
        back_button = QPushButton('back')
        back_button.clicked.connect(self.back_button_click)

        self.setting_area.addWidget(icon, 1)
        self.setting_area.addWidget(empty, 7)
        self.setting_area.addWidget(set_button, 1)
        self.setting_area.addWidget(back_button, 1)

        #changeable area
        self.content_area = FurnaceSelectArea(self.dyn_content, self.sock)

        # for i in range(parameter.total_furnace):
        #     self.content_area.furnace_area.itemAt(i).set

        self.dyn_content.addWidget(self.content_area)
        self.furnace_list = []
        for i in range(parameter.total_furnace):
            self.furnace_list.append(furnacePage.FurnaceContent(i+1, self.sock, self.dbconn, self.combo_opt))
            self.dyn_content.addWidget(self.furnace_list[i])
        
        self.dyn_content.addWidget(SettingPage(self.combo_opt))

        #test area
        working_process = apply_exist_process(self.dbconn, self.furnace_list)

        # #add working_process to monitoring
        # self.monitoring_thread = threading.Thread(target=thread.monitoring, args=(self.dbconn, self.furnace_list, working_process))
        # self.monitoring_thread.daemon = True
        # self.monitoring_thread.start()

        #add working_process to monitoring
        self.monitoring_thread = thread.Monitoring(self.dbconn, working_process)
        self.monitoring_thread.update_sensor.connect(self.update_signal_function)
        self.monitoring_thread.nature_end.connect(self.nature_end_signal_function)
        self.monitoring_thread.clear_signal.connect(self.clear_signal_function)
        self.monitoring_thread.start()

        #test area
        self.endprocess_survey = threading.Thread(target=thread.endprocess_survey, args=(self.OutputReceiver_instance,))
        self.endprocess_survey.daemon = True
        self.endprocess_survey.start()

        self.mainlayout.addLayout(self.setting_area, 1)
        self.mainlayout.addWidget(self.dyn_content, 10)

        self.setLayout(self.mainlayout)
        self.setWindowTitle('CPS ProtoType')
        self.setGeometry(0, 0, parameter.width, parameter.height)
    
    def back_button_click(self):
        self.dyn_content.setCurrentIndex(0)
        self.sock.sendall('esc'.encode())

        recv_msg = self.sock.recv(1024).decode()


    def set_button_click(self):
        self.dyn_content.setCurrentIndex(parameter.total_furnace + 1)

    def update_signal_function(self, index, sensor):
        self.furnace_list[index].signal(sensor)

    def nature_end_signal_function(self, index):
        self.furnace_list[index].stop_process_nature()
    
    def clear_signal_function(self, index):
        self.furnace_list[index].sensor_area.clear()

def apply_exist_process(dbconn, furnace_pages):
    """
    client를 실행하기 전 이미 진행중이던 공정에 대해 센서값들을 읽어와 변수에 할당

    dbconn(database connector)
    furnace_pagse(list) : list of furnacePage instance
    """
    dbcur = dbconn.cursor()
    processes = utils.get_working_process(dbcur)

    for i in range(parameter.total_furnace):
        if processes[i] == '-':
            continue

        sql = """select * from furnace""" + str(i + 1) +  """ where id = '""" + processes[i] + """' order by current desc limit 50"""
        dbcur.execute(sql)
        sensors = list(dbcur.fetchall())
        sensors.reverse()
        for sensor in sensors:
            sensor = list(sensor)

        sql = """select * from process where id = '""" + processes[i] + """'"""
        dbcur.execute(sql)
        process_setting = list(dbcur.fetchall()[0]) 

        furnace_pages[i].apply_exist_process(process_setting, sensors)   
    dbcur.close()
    return processes
