from setting_content import SettingContent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
import pymysql
import threading
import time
import json

import client
import button
import parameter
import furnacePage
import utils
import thread

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

        #except setting area
        self.layout.addWidget(self.image_area)
        self.layout.addLayout(self.furnace_area)
        self.setLayout(self.layout)

    def furnace_button_click(self, number:int):
        self.stk_w.setCurrentIndex(number)
        send_msg = 'num ' + str(number)
        self.sock.sendall(send_msg.encode())

        recv_msg = self.sock.recv(1024).decode()
        recv_msg_list = recv_msg.split()
        state = recv_msg_list[0]
        process = None
        if len(recv_msg_list) != 1:
            process = recv_msg_list[1]

        self.stk_w.widget(number).SetStateText(state, process)

    
class HomePage(QWidget):
    def __init__(self, C, dbconn):
        super().__init__()
        self.sock = C.sock
        self.dbconn = dbconn

        self.processes_id = []
        #load combobox content from json file test
        with open(parameter.json_path, 'r') as combo_json:
            self.combo_opt = json.load(combo_json)
            self.processes_id.append('-')
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
        set_button.clicked.connect(self.set_button_click)
        back_button = QPushButton('back')
        back_button.clicked.connect(self.back_button_click)

        self.setting_area.addWidget(icon, 1)
        self.setting_area.addWidget(empty, 7)
        self.setting_area.addWidget(set_button, 1)
        self.setting_area.addWidget(back_button, 1)

        #changeable area
        self.content_area = Select(self.dyn_content, self.sock)

        # for i in range(parameter.total_furnace):
        #     self.content_area.furnace_area.itemAt(i).set

        self.dyn_content.addWidget(self.content_area)
        self.furnace_list = []
        for i in range(parameter.total_furnace):
            self.furnace_list.append(furnacePage.FurnaceContent(i+1, self.sock, self.dbconn, self.combo_opt))
            self.dyn_content.addWidget(self.furnace_list[i])
        
        self.dyn_content.addWidget(SettingContent(self.combo_opt))

        #test area
        working_process = apply_exist_process(self.dbconn, self.furnace_list)

        #add working_process to monitoring
        t = threading.Thread(target=thread.monitoring, args=(self.dbconn, self.furnace_list, working_process))
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


    def set_button_click(self):
        self.dyn_content.setCurrentIndex(parameter.total_furnace + 1)


def apply_exist_process(dbconn, furnace_pages):
    """
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