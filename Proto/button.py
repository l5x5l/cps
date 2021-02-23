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

#set base element about process and send them to server
def set_base_button_click(material:str, process:str, amount:str):
    print(material + ' / ' + process+ " / "+ amount)

#set base element about process and send them to server
def set_detail_button_click(gas:str, tempers = [], times = []):
    print(gas)


def back_button_click(stk_w):
    stk_w.setCurrentIndex(0)

def furnace_button_click(stk_w, index:int):
    stk_w.setCurrentIndex(index)