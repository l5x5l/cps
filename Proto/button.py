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

        self.setCheckable(True)


    def custom_toggle(self):
        self.now_start_button = not self.now_start_button
        self.setStyleSheet("background-color: %s" % (self.colors[self.now_start_button]))
        self.setText(self.texts[self.now_start_button])

    def button_click(self, material:str, process:str, amount:str, sock, disable_list, able_list):
        """
        disable_list : disable widgets when button is start button (so, this widgets are able when button is modify button)
        able_list : able widgets when button is start button (so, this widgets area disable when button is modify button)
        """
        msg = ('base ' + material + ' / ' + process+ " / "+ amount)
        msg_byte = msg.encode()
        sock.sendall(msg_byte)

        recv_msg = sock.recv(1024).decode()
        print(recv_msg)
        '''
        if recv_msg != parameter.success_str:
            print(recv_msg)
            return
        '''
        self.custom_toggle()
        for elem in disable_list:
            elem.setEnabled(not self.now_start_button)
        
        for elem in able_list:
            elem.setEnabled(self.now_start_button)



class Detail_Button(QPushButton):
    def __init__(self, text):
        QPushButton.__init__(self, text)
        self.colors = {True:'green', False:'orange'}
        self.texts = {True: parameter.decision_str, False: parameter.modify_str}
        self.now_start_button = True
        self.setStyleSheet("background-color: green")

        self.setCheckable(True)


    def custom_toggle(self):
        self.now_start_button = not self.now_start_button
        self.setStyleSheet("background-color: %s" % (self.colors[self.now_start_button]))
        self.setText(self.texts[self.now_start_button])


    def button_click(self, gas:str, tempers:list, times:list, sock, disable_list, able_list):
        msg_byte = ('detail ' + gas).encode()
        sock.sendall(msg_byte)

        recv_msg = sock.recv(1024).decode()
        print(recv_msg)
        '''
        if recv_msg != parameter.success_str:
            print(recv_msg)
            return
        '''
        self.custom_toggle()
        for elem in disable_list:
            elem.setEnabled(not self.now_start_button)
        
        for elem in able_list:
            elem.setEnabled(self.now_start_button)


def back_button_click(stk_w, sock):
    stk_w.setCurrentIndex(0)
    sock.sendall('esc'.encode())

    recv_msg = sock.recv(1024).decode()
    print(recv_msg)

def furnace_button_click(stk_w, sock, number:int):
    stk_w.setCurrentIndex(number)
    send_msg = 'num ' + str(number)
    sock.sendall(send_msg.encode())

    recv_msg = sock.recv(1024).decode()
    print(recv_msg)