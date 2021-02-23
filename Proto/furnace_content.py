import parameter
import button
import client
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation

import random

class PlotCanvas(FigureCanvas):
    def __init__(self, parent = None, width = 5, height = 4, dpi = 100):
        fig = Figure()

        self.temp1 = fig.add_subplot(421, xlim=(0, 50), ylim=(0, 1024))
        self.temp2 = fig.add_subplot(422, xlim=(0, 50), ylim=(0, 1024))
        self.temp3 = fig.add_subplot(423, xlim=(0, 50), ylim=(0, 1024))
        self.temp4 = fig.add_subplot(424, xlim=(0, 50), ylim=(0, 1024))
        self.temp5 = fig.add_subplot(425, xlim=(0, 50), ylim=(0, 1024))
        self.temp6 = fig.add_subplot(426, xlim=(0, 50), ylim=(0, 1024))
        self.flow = fig.add_subplot(427, xlim=(0, 50), ylim=(0, 1024))
        self.press = fig.add_subplot(428,xlim=(0, 50), ylim=(0, 1024))

        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
    

    def compute_initial_figure(self):
        pass

class SensorPlot(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
        vbox = QVBoxLayout()
        self.canvas = PlotCanvas(self, width=10, height=8, dpi=100)
        vbox.addWidget(self.canvas)
        hbox = QHBoxLayout()
        '''
        self.start_button = QPushButton("start", self)
        self.stop_button = QPushButton("stop", self)
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)
        hbox.addWidget(self.start_button)
        hbox.addWidget(self.stop_button)
        '''
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.list = [self.canvas.temp1, self.canvas.temp2, self.canvas.temp3, self.canvas.temp4, self.canvas.temp5, self.canvas.temp6,self.canvas.flow, self.canvas.press]
        self.line = ["", "", "", "", "", "", "", ""]
        
        for i in range(len(self.list)):              
            self.x = np.arange(50)
            self.y = np.ones(50, dtype=np.float)*np.nan
            self.line[i], = self.list[i].plot(self.x, self.y, animated=True)

        self.ani = animation.FuncAnimation(self.canvas.figure, self.update_line,blit=True, interval=1000)
        self.ani2 = animation.FuncAnimation(self.canvas.figure, self.update_line2,blit=True, interval=1000)
    

    def update_line(self, i):
        y = random.randint(0,1024)
        old_y = self.line[4].get_ydata()
        new_y = np.r_[old_y[1:], y]
        self.line[4].set_ydata(new_y)
        
        # self.line.set_ydata(y)
        return [self.line[4]]

    def update_line2(self, i):
        y2 = random.randint(0,510)
        old_y2 = self.line[3].get_ydata()
        new_y2 = np.r_[old_y2[1:], y2]
        self.line[3].set_ydata(new_y2)
        return [self.line[3]]
        # self.line.set_ydata(y)

    def on_start(self):
        self.ani = animation.FuncAnimation(self.canvas.figure, self.update_line,blit=True, interval=1000)
        self.ani2 = animation.FuncAnimation(self.canvas.figure, self.update_line2,blit=True, interval=1000)

    def on_stop(self):
        self.ani._stop()
        self.ani2._stop()

class FurnaceContent(QWidget):
    def __init__(self, furnace_number:int, sock):
        super().__init__()
        self.number = furnace_number
        self.sock = sock
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()
        #left area : sensor data (temp1~6, flow, press)
        self.sensor_area = SensorPlot()

        #middle area : furnace image and sensor data
        self.middle_area = QVBoxLayout()
        furnace_img = QWidget()
        furnace_number = QLabel(str(self.number))
        self.middle_area.addWidget(furnace_number)
        self.middle_area.addWidget(furnace_img)

        #right_area : select base element and detail element
        self.right_area = QVBoxLayout()
        
        #base element setting
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

        set_base_button = button.Button(parameter.decision_str)
        set_base_button.clicked.connect(lambda:self.set_base_button_click(str(material_opt.currentText()), str(process_opt.currentText()), str(amount_opt.currentText())))

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

        set_detail_button = button.Button(parameter.decision_str)
        set_detail_button.clicked.connect(lambda:self.set_detail_button_click(str(gas_opt.currentText())))
        
        detail_area.addWidget(set_temper_time_button)
        detail_area.addWidget(gas_opt)
        detail_area.addWidget(set_detail_button)

        self.right_area.addLayout(base_area,2)
        self.right_area.addLayout(detail_area,2)

        #concat
        self.layout.addWidget(self.sensor_area,2)
        self.layout.addLayout(self.middle_area, 1)
        self.layout.addLayout(self.right_area, 1)

        self.setLayout(self.layout)


    #set base element about process and send them to server
    def set_base_button_click(self, material:str, process:str, amount:str):
        msg = ('base ' + material + ' / ' + process+ " / "+ amount)
        msg_byte = msg.encode()
        self.sock.sendall(msg_byte)

        recv_msg = self.sock.recv(1024).decode()
        print(recv_msg)


    #set base element about process and send them to server
    def set_detail_button_click(self, gas:str, tempers = [], times = []):
        msg_byte = ('detail ' + gas).encode()
        self.sock.sendall(msg_byte)

        recv_msg = self.sock.recv(1024).decode()
        print(recv_msg)

    def set_detail_temp_time_click(self):
        win = SubWindow()
        r = win.showModel()

        if r:
            value = win.test_opt.currentText()
            print(value)

#테스트용 subwindow, 이걸 온도/시간 상세설정 페이지로 전환하여야 함
class SubWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet('background-color:white')
        self.setWindowTitle('Sub Window')
        self.setGeometry(100, 100, 800, 400)

        layout = QVBoxLayout()


        self.test_opt = QComboBox(self)
        self.test_opt.addItem('1a')
        self.test_opt.addItem('2b')
        self.test_opt.addItem('3c')

        btnOK = QPushButton("확인")
        btnOK.clicked.connect(self.OKbutton_click)
        btnCancel = QPushButton("취소")
        btnCancel.clicked.connect(self.Cancelbutton_click)

        layout.addWidget(self.test_opt)
        layout.addWidget(btnOK)
        layout.addWidget(btnCancel)

        self.setLayout(layout)


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