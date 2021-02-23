import sys
import parameter

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *

class Button(QPushButton):
    def __init__(self, text):
        QPushButton.__init__(self, text)
        self.setStyleSheet("background-color: green")

        self.setCheckable(True)
        self.toggled.connect(self.slot_toggle)

    @pyqtSlot(bool)
    def slot_toggle(self, state):
        self.setStyleSheet("background-color: %s" % ({True: "green", False: "red"}[state]))
        self.setText({True: parameter.decision_str, False: parameter.modify_str}[state])


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