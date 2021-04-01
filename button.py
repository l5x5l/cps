import sys
import parameter
import socket

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *

class Base_Button(QPushButton):
    def __init__(self, text):
        QPushButton.__init__(self, text)
        self.colors = {True:'green', False:'orange'}
        self.texts = {True: parameter.decision_str, False: parameter.modify_str}
        self.now_start_button = True
        self.setStyleSheet("background-color: green")
        self.able_list = None
        self.disable_list = None
        self.base_opt = 'base'

        self.setCheckable(True)

    def set_state_start(self):
        self.now_start_button = True
        self.setStyleSheet("background-color: %s" % (self.colors[self.now_start_button]))
        self.setText(self.texts[self.now_start_button])
        self.base_opt = 'base'

    def set_state_fix(self):
        self.now_start_button = False
        self.setStyleSheet("background-color: %s" % (self.colors[self.now_start_button]))
        self.setText(self.texts[self.now_start_button])
        self.base_opt = 'base_fix'

    def custom_toggle(self):
        self.now_start_button = not self.now_start_button
        self.setStyleSheet("background-color: %s" % (self.colors[self.now_start_button]))
        self.setText(self.texts[self.now_start_button])

        if self.now_start_button:
            self.base_opt = 'base'
        else:
            self.base_opt = 'base_fix'


    def set_change_widget_list(self, disable_list, able_list):
        self.able_list = able_list
        self.disable_list = disable_list


    def button_click(self, material:str, process:str, amount:str, sock):
        """
        disable_list : disable widgets when button is start button (so, this widgets are able when button is modify button)
        able_list : able widgets when button is start button (so, this widgets area disable when button is modify button)
        """
        if self.now_start_button:
            msg = (self.base_opt + ' ' + material + ' ' + process+ ' ' + amount)
        else:
            msg = self.base_opt

        msg_byte = msg.encode()
        sock.sendall(msg_byte)

        recv_msg = sock.recv(1024).decode()

        self.custom_toggle()
        for elem in self.disable_list:
            elem.setEnabled(not self.now_start_button)
        
        for elem in self.able_list:
            elem.setEnabled(self.now_start_button)



class Detail_Button(QPushButton):
    def __init__(self, text):
        QPushButton.__init__(self, text)
        self.colors = {True:'green', False:'orange'}
        self.texts = {True: parameter.decision_str, False: parameter.modify_str}
        self.now_start_button = True
        self.setStyleSheet("background-color: green")
        self.able_list = None
        self.disable_list = None
        self.base_opt = 'detail'

        #아 변수명을 뭘로 하지
        self.is_process_wokring = False

        self.setCheckable(True)

    def set_state_start(self):  #using when clear UI
        self.now_start_button = True
        self.setStyleSheet("background-color: %s" % (self.colors[self.now_start_button]))
        self.setText(self.texts[self.now_start_button])
        self.base_opt = 'detail'

        self.is_process_wokring = False
        
    def set_state_fix(self):
        self.now_start_button = False
        self.setStyleSheet("background-color: %s" % (self.colors[self.now_start_button]))
        self.setText(self.texts[self.now_start_button])
        self.base_opt = 'detail_fix'

        self.is_process_wokring = True

    def custom_toggle(self):
        self.now_start_button = not self.now_start_button
        self.setStyleSheet("background-color: %s" % (self.colors[self.now_start_button]))
        self.setText(self.texts[self.now_start_button])

        ##test function (add base_opt = 'restart')
        if self.now_start_button:
            if self.is_process_wokring:
                self.base_opt = 'restart'
            else:
                self.base_opt = 'detail'
        else:
            self.is_process_wokring = True
            self.base_opt = 'detail_fix'

    def set_change_widget_list(self, disable_list, able_list):
        self.able_list = able_list
        self.disable_list = disable_list

    def button_click(self, gas:str, tempers:list, heattimes:list, staytimes:list, sock):
        count = len(tempers)

        local_tempers = list(map(str, tempers))
        local_heattimes = list(map(str, heattimes))
        local_staytimes = list(map(str, staytimes))

        heattime = ' '.join(local_heattimes)
        staytime = ' '.join(local_staytimes)
        temper = ' '.join(local_tempers)
        
        if self.now_start_button:
            msg = self.base_opt + ' ' + str(count) + ' ' + temper + ' ' + heattime + ' ' + staytime + ' ' + gas
        else:
            msg = self.base_opt

        msg_byte = msg.encode()
        sock.sendall(msg_byte)

        recv_msg = sock.recv(1024).decode()

        self.custom_toggle()
        for elem in self.disable_list:
            elem.setEnabled(not self.now_start_button)
        
        for elem in self.able_list:
            elem.setEnabled(self.now_start_button)