import sys
import parameter
import json
import button
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap

class SettingPage(QWidget):
    """
    setting page which modify qcombobox items in furnace pages
    """
    def __init__(self, combo_opt):
        """
        combo_opt is dictionary which contain qcombobox items
        [ex] {'material' : ['material1', 'material2', 'material3']}
        """
        QMainWindow.__init__(self)
        self.combobox_opt = combo_opt
        self.initUI()

    def initUI(self):
        self.setStyleSheet('background-color:white')
        self.base_box = QHBoxLayout()
        self.right_area = QGridLayout()
        self.left_area = QVBoxLayout()
        self.popup = ConfirmWindow()

        self.domains = ['material', 'process', 'amount', 'gas']
        self.QLines = {'material':None, 'process':None, 'amount':None, 'gas':None}
        
        for domain in self.domains:
            self.QLines[domain] = self.set_combobox(domain, self.combobox_opt[domain])

        self.right_area.addLayout(self.QLines['material'], 0, 0)
        self.right_area.addLayout(self.QLines['process'], 0, 1)
        self.right_area.addLayout(self.QLines['amount'], 1, 0)
        self.right_area.addLayout(self.QLines['gas'], 1, 1)

        btn_OK = QPushButton(parameter.confirm_str)
        btn_OK.clicked.connect(self.OKbutton_click)
        btn_CAN = QPushButton(parameter.cancel_str)
        

        self.left_area.addWidget(btn_OK)
        self.left_area.addWidget(btn_CAN)

        self.base_box.addLayout(self.left_area)
        self.base_box.addLayout(self.right_area)

        self.setLayout(self.base_box)
        self.setWindowTitle('CPS ProtoType')
        self.setGeometry(0, 0, parameter.width, parameter.height)

    def one_row(self, text:str, domain:str):
        row = QHBoxLayout()
        option_input = QLineEdit(text)
        btnDel = QPushButton(parameter.del_str)

        row.addWidget(option_input)
        row.addWidget(btnDel)
        row.itemAt(1).widget().clicked.connect(lambda:self.Delbutton_click(row, domain))    #row.itemAt(1).widget() = btnDel

        return row

    def set_combobox(self, domain:str, option_list:list):
        """
        domain is string, one of 'materail', 'process', 'amount', 'gas'
        option_list is qcombobox of domain
        """
        setting_area = QVBoxLayout()
        rows = QVBoxLayout()
        btnAdd = QPushButton(parameter.add_str)
        btnAdd.clicked.connect(lambda:self.Addbutton_click(domain))


        for elem in option_list:
            row = self.one_row(elem, domain)
            row.itemAt(0).widget().setEnabled(False)
            rows.addLayout(row)


        setting_area.addLayout(rows)
        setting_area.addWidget(btnAdd)
        return setting_area
        
    def Delbutton_click(self, widget, domain):
        """
        click event handler function of btnDel, which deletes textline row
        """
        count = self.QLines[domain].itemAt(0).count()

        if count >= 2:
            for i in reversed(range(widget.count())):
                widget.itemAt(i).widget().setParent(None)
            self.QLines[domain].removeItem(widget)

    def Addbutton_click(self, domain):
        """
        click event handler function of btnAdd, which add row in row_area (rows)
        """
        count = self.QLines[domain].itemAt(0).count()
        if count <= 10:
            self.QLines[domain].itemAt(0).addLayout(self.one_row("", domain))

    def OKbutton_click(self):
        """
        click event handler function of btn_OK which adjust qcombobox items
        """
        win = self.popup
        r = win.showModel()

        if r:
            for domain in self.domains:
                count = self.QLines[domain].itemAt(0).count()
                items = [self.QLines[domain].itemAt(0).itemAt(i).itemAt(0).widget().text() for i in range(count)]
                self.combobox_opt[domain] = items

            with open(parameter.json_path, 'w') as combo_json:
                json.dump(self.combobox_opt, combo_json)


class ConfirmWindow(QDialog):
    """
    popup window which ask adjust qcombobox item setting
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet('background-color:white')
        self.setWindowTitle('Sub Window')
        self.setGeometry(100, 100, 500, 300)

        self.layout = QVBoxLayout()
        self.buttons = QHBoxLayout()
        self.text = QLabel('정말 수정하시겠습니까?\n수정한 내용은 재실행시 반영됩니다')

        btn_OK = QPushButton(parameter.confirm_str)
        btn_OK.clicked.connect(self.OKbutton_click)
        btn_CAN = QPushButton(parameter.cancel_str)
        btn_CAN.clicked.connect(self.Cancelbutton_click)

        self.buttons.addWidget(btn_OK)
        self.buttons.addWidget(btn_CAN)

        self.layout.addWidget(self.text)
        self.layout.addLayout(self.buttons)
        self.setLayout(self.layout)

    def OKbutton_click(self):
        self.accept()

    def Cancelbutton_click(self):
        self.reject()

    def showModel(self):
        return super().exec_()

