import parameter
import button
import client
import sys
import pymysql
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation

import random

class PlotCanvas(FigureCanvas):
    def __init__(self, parent = None, width = 5, height = 4, dpi = 100):
        self.fig = Figure()

        self.temp1 = self.fig.add_subplot(421, xlim=(0, 50), ylim=(0, 1024))
        self.temp2 = self.fig.add_subplot(422, xlim=(0, 50), ylim=(0, 1024))
        self.temp3 = self.fig.add_subplot(423, xlim=(0, 50), ylim=(0, 1024))
        self.temp4 = self.fig.add_subplot(424, xlim=(0, 50), ylim=(0, 1024))
        self.temp5 = self.fig.add_subplot(425, xlim=(0, 50), ylim=(0, 1024))
        self.temp6 = self.fig.add_subplot(426, xlim=(0, 50), ylim=(0, 1024))
        self.flow = self.fig.add_subplot(427, xlim=(0, 50), ylim=(0, 1024))
        self.press = self.fig.add_subplot(428,xlim=(0, 50), ylim=(0, 1024))

        self.compute_initial_figure()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

    def compute_initial_figure(self):
        pass

class SensorPlot(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)

        self.base_box = QHBoxLayout()

        self.left_area = QVBoxLayout()
        self.canvas = PlotCanvas(self, width=10, height=8, dpi=100)
        self.left_area.addWidget(self.canvas)

        #middle area에도 센서값을 표시하는 구역이 존재하므로 통합
        self.middle_area = QVBoxLayout()
        furnace_img = QWidget()

        furnace_number = QLabel('testing')

        self.middle_area.addWidget(furnace_number)
        self.middle_area.addWidget(furnace_img)


        self.base_box.addLayout(self.left_area, 2)
        self.base_box.addLayout(self.middle_area, 1)

        self.setLayout(self.base_box)

        self.list = [self.canvas.temp1, self.canvas.temp2, self.canvas.temp3, self.canvas.temp4, self.canvas.temp5, self.canvas.temp6,self.canvas.flow, self.canvas.press]
        self.line = ["", "", "", "", "", "", "", ""]
        
        for i in range(len(self.list)):              
            self.x = np.arange(50)
            self.y = np.ones(50, dtype=np.float)*np.nan
            self.line[i], = self.list[i].plot(self.x, self.y, animated=False)
    
    def init_data(self, datas):
        """
        update total graph of one furnace

        datas : sensor datas -> [[temp1~6, flow, press, touch], [temp1~6, flow, press, touch], [temp1~6, flow, press, touch],...]
        type of datas elemnt : list([int, int, ..., str])
        """
        sensor_list = []
        temp1, temp2, temp3, temp4, temp5, temp6, flow, press = [], [], [], [], [], [], [], []
        for value in datas:
            temp1.append(int(value[0]))
            temp2.append(int(value[1]))
            temp3.append(int(value[2]))
            temp4.append(int(value[3]))
            temp5.append(int(value[4]))
            temp6.append(int(value[5]))
            flow.append(int(value[6]))
            press.append(int(value[7]))

        init_sensor_size = len(temp1)

        sensor_list.append(temp1)
        sensor_list.append(temp2)
        sensor_list.append(temp3)
        sensor_list.append(temp4)
        sensor_list.append(temp5)
        sensor_list.append(temp6)
        sensor_list.append(flow)
        sensor_list.append(press)

        for index, _ in enumerate(self.line):
            y = sensor_list[index]
            old_y = self.line[index].get_ydata()
            new_y = np.r_[old_y[init_sensor_size:], y]
            self.line[index].set_ydata(new_y)
        
        self.canvas.draw()
        self.canvas.flush_events()


    def update(self, datas):
        """
        update total graph of one furnace

        datas : sensor data -> [temp1~6, flow, press, touch]
        type of datas elemnt without touch : int
        """
        #print(self.line[0].get_ydata())
        #print(datas)
        for index, _ in enumerate(self.line):
            #가장 앞에 있는게 touch 인듯
            y = int(datas[index + 3])
            #y = random.randint(0,1024)
            old_y = self.line[index].get_ydata()
            new_y = np.r_[old_y[1:], y]
            self.line[index].set_ydata(new_y)

        self.canvas.draw()
        self.canvas.flush_events()


class FurnaceContent(QWidget):
    def __init__(self, furnace_number:int, sock, dbconn):
        super().__init__()
        self.setting_popup = SubWindow()
        self.number = furnace_number
        self.sock = sock
        self.dbconn = dbconn
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()

        detail_disable = []
        detail_able = []
        base_disable = []
        base_able = []

        #left area : sensor data (temp1~6, flow, press)
        self.sensor_area = SensorPlot()
        '''
        #middle area : furnace image and sensor data
        self.middle_area = QVBoxLayout()
        furnace_img = QWidget()
        furnace_number = QLabel(str(self.number))
        self.middle_area.addWidget(furnace_number)
        self.middle_area.addWidget(furnace_img)
        '''
        #right_area : select base element and detail element
        self.right_area = QVBoxLayout()
        
        #base element setting
        #버튼은 마지막에 layout에 추가하기 직전에 추가된다.  
        base_area = QVBoxLayout()
        material_opt = QComboBox(self)
        material_opt.addItem('material1')
        material_opt.addItem('material2')
        material_opt.addItem('material3')

        process_opt = QComboBox(self)
        process_opt.addItem('process1')
        process_opt.addItem('process2')
        process_opt.addItem('process3')

        amount_opt = QComboBox(self)
        amount_opt.addItem('300')
        amount_opt.addItem('500')
        amount_opt.addItem('700')

        set_base_button = button.Base_Button(parameter.decision_str)

        base_area.addWidget(material_opt)
        base_area.addWidget(process_opt)
        base_area.addWidget(amount_opt)
        base_area.addWidget(set_base_button)

        #detail element setting
        detail_area = QVBoxLayout()

        set_temper_time_button = QPushButton('시간/온도 상세설정')
        set_temper_time_button.clicked.connect(self.set_detail_temp_time_click)

        gas_opt = QComboBox(self)
        gas_opt.addItem('gas1')
        gas_opt.addItem('gas2')
        gas_opt.addItem('gas3')

        set_detail_button = button.Detail_Button(parameter.decision_str)

        detail_area.addWidget(set_temper_time_button)
        detail_area.addWidget(gas_opt)
        detail_area.addWidget(set_detail_button)       

        '''
        base_able.append(material_opt)
        base_able.append(process_opt)
        base_able.append(amount_opt)
        base_disable.append(set_temper_time_button)
        base_disable.append(gas_opt)
        base_disable.append(set_detail_button)

        detail_able.append(set_base_button)
        detail_able.append(gas_opt)
        detail_able.append(set_temper_time_button)
        '''
        base_area.itemAt(3).widget().clicked.connect(lambda:set_base_button.button_click(str(material_opt.currentText()), str(process_opt.currentText()), str(amount_opt.currentText()), self.sock, base_disable, base_able))
        detail_area.itemAt(2).widget().clicked.connect(lambda:set_detail_button.button_click(str(gas_opt.currentText()), [], [], self.sock, detail_disable, detail_able))

        self.right_area.addLayout(base_area,2)
        self.right_area.addLayout(detail_area,2)

        #concat
        self.layout.addWidget(self.sensor_area,3)
        self.layout.addLayout(self.right_area, 1)

        self.setLayout(self.layout)


    #set base element about process and send them to server
    def set_base_button_click(self, material:str, process:str, amount:str):
        msg = ('base ' + material + ' / ' + process+ " / "+ amount)
        msg_byte = msg.encode()
        self.sock.sendall(msg_byte)

        #success msg
        recv_msg = self.sock.recv(1024).decode()



    #set base element about process and send them to server
    def set_detail_button_click(self, gas:str, tempers = [], times = []):
        msg_byte = ('detail ' + gas).encode()
        self.sock.sendall(msg_byte)

        #success msg
        recv_msg = self.sock.recv(1024).decode()


    def set_detail_temp_time_click(self):
        win = self.setting_popup
        r = win.showModel()

        if r:
            time = win.setting_area.itemAt(0).itemAt(0).widget().text()
            temp = win.setting_area.itemAt(0).itemAt(1).widget().text()
            value = str(time) + "/" + str(temp)
            print(value)

#테스트용 subwindow, 이걸 온도/시간 상세설정 페이지로 전환하여야 함
class SubWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.temp_times = []
        self.initUI()

    
    def initUI(self):
        self.setting_list = []
        self.setStyleSheet('background-color:white')
        self.setWindowTitle('Sub Window')
        self.setGeometry(100, 100, 800, 400)

        self.layout = QHBoxLayout()

        self.graph_area = QWidget()

        self.setting_button = QVBoxLayout()
        self.setting_area = QVBoxLayout()
        self.button_area = QVBoxLayout()
        '''
        self.test_opt = setting_row()
        self.test_opt.addItem('1a')
        self.test_opt.addItem('2b')
        self.test_opt.addItem('3c')
        '''

        btnOK = QPushButton("확인")
        btnOK.clicked.connect(self.OKbutton_click)
        btnCancel = QPushButton("취소")
        btnCancel.clicked.connect(self.Cancelbutton_click)
        btnAdd = QPushButton("추가")
        btnAdd.clicked.connect(self.Addbutton_click)

        self.setting_area.addLayout(self.setting_row())
        self.button_area.addWidget(btnAdd)
        self.button_area.addWidget(btnOK)
        self.button_area.addWidget(btnCancel)

        self.setting_button.addLayout(self.setting_area, 5)
        self.setting_button.addLayout(self.button_area, 3)

        self.layout.addWidget(self.graph_area)
        self.layout.addLayout(self.setting_button)

        self.setLayout(self.layout)

    def setting_row(self):
        row = QHBoxLayout()  
        number = self.setting_area.count()
        time_input = QLineEdit(self)
        temp_input = QLineEdit(self)
        btnDel = QPushButton('삭제')
        row.addWidget(time_input, 4)
        row.addWidget(temp_input, 4)
        row.addWidget(btnDel, 1)
        row.itemAt(2).widget().clicked.connect(lambda:self.Delbutton_click(row))

        return row

    def test_del(self):
        pass


    def all_delete(self):
        for i in reversed(range(self.setting_area.count())):
            self.setting_area.itemAt(i).widget()


    def Addbutton_click(self):
        if self.setting_area.count() < 10:
            self.setting_area.addLayout(self.setting_row())

    ##주의사항 : layout을 제거할 때는 layout내의 widget을 먼저 모두 제거해야 한다.
    def Delbutton_click(self, widget):
        count = self.setting_area.count()
        print(count)
        if count >= 2:
            for i in reversed(range(widget.count())):
                widget.itemAt(i).widget().setParent(None)
            self.setting_area.removeItem(widget)
            '''
            print(self.setting_area.itemAt(0).itemAt(number))
            print(self.layout.itemAt(1).itemAt(0).itemAt(number))
            print(self.layout.count())
            '''


    def OKbutton_click(self):
        self.accept()

    def Cancelbutton_click(self):
        self.reject()

    def showModel(self):
        return super().exec_()
        


if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    fc = FurnaceContent()
    fc.show()
    sys.exit(qApp.exec_())