import parameter
import button
import client
import sys
import pymysql
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation

import random

class SensorPlotCanvas(FigureCanvas):
    """
    group of plots which represent sensor value in realtime
    """
    def __init__(self, parent = None, width = 5, height = 4, dpi = 100):
        self.fig = Figure()

        self.temp1 = self.fig.add_subplot(421, xlim=(0, 50), ylim=(0, 1024))
        self.temp2 = self.fig.add_subplot(422, xlim=(0, 50), ylim=(0, 1024))
        self.temp3 = self.fig.add_subplot(423, xlim=(0, 50), ylim=(0, 1024))
        self.temp4 = self.fig.add_subplot(424, xlim=(0, 50), ylim=(0, 1024))
        self.temp5 = self.fig.add_subplot(425, xlim=(0, 50), ylim=(0, 1024))
        self.temp6 = self.fig.add_subplot(426, xlim=(0, 50), ylim=(0, 1024))
        self.flow = self.fig.add_subplot(427, xlim=(0, 50), ylim=(0, 100))
        self.press = self.fig.add_subplot(428, xlim=(0, 50), ylim=(0, 100))

        self.compute_initial_figure()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.draw()
        self.flush_events()

    def compute_initial_figure(self):
        pass

class SensorPlot(QWidget):
    """
    layout which represents sensor values in plot and table

    base_box : main layout of SensorPlot
    left_area : represents 8 sensor value on plot form
    middle_area : represents 4 sensor value on table form 
    """
    def __init__(self):
        QMainWindow.__init__(self)

        self.base_box = QHBoxLayout()

        self.left_area = QVBoxLayout()
        self.canvas = SensorPlotCanvas(self, width=10, height=8, dpi=100)
        self.left_area.addWidget(self.canvas)

        #middle area에도 센서값을 표시하는 구역이 존재하므로 통합
        self.middle_area = QVBoxLayout()
        furnace_img = QLabel()
        furnace_img.setPixmap(QPixmap('.\\images\\furnace.png'))

        sensor_text_area = QTableWidget(self) #나중에 세부적으로 설정할 예정

        self.middle_area.addWidget(furnace_img, 7)
        self.middle_area.addWidget(sensor_text_area, 3)


        self.base_box.addLayout(self.left_area, 2)
        self.base_box.addLayout(self.middle_area, 1)

        self.setLayout(self.base_box)

        self.list = [self.canvas.temp1, self.canvas.temp2, self.canvas.temp3, self.canvas.temp4, self.canvas.temp5, self.canvas.temp6,self.canvas.flow, self.canvas.press]
        self.line = ["", "", "", "", "", "", "", ""]    #None 대신 ""을 사용함
        
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
            temp1.append(int(value[3]))
            temp2.append(int(value[4]))
            temp3.append(int(value[5]))
            temp4.append(int(value[6]))
            temp5.append(int(value[7]))
            temp6.append(int(value[8]))
            flow.append(int(value[9]))
            press.append(int(value[10]))

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

        for index, _ in enumerate(self.line):
            #가장 앞에 있는게 touch 인듯
            y = int(datas[index + 3])
            #y = random.randint(0,1024)
            old_y = self.line[index].get_ydata()
            new_y = np.r_[old_y[1:], y]
            self.line[index].set_ydata(new_y)

        self.canvas.draw()
        self.canvas.flush_events()


class SettingPlotCanvas(FigureCanvas):
    """
    plot which represents detail temperature and time setting 
    """
    def __init__(self, parent=None, width = 5, height = 4, dpi = 100):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111, xlim=(0,50), ylim=(0,1000))
        self.compute_initial_figure()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

    def compute_initial_figure(self):
        pass



class SettingPlot(QWidget):
    """
    layout which represent detail temperature and time setting plot 
    """
    def __init__(self):
        QMainWindow.__init__(self)
        self.base_box = QVBoxLayout()
        self.canvas = SettingPlotCanvas(self, 10, 8, 100)
        self.plot, = self.canvas.ax.plot([0],[0], animated=False)
        self.base_box.addWidget(self.canvas)
        self.setLayout(self.base_box)
        self.canvas.draw()

    def update(self, x, y):
        self.canvas.ax.set_xlim(0, x[-1])
        self.canvas.ax.set_ylim(0, max(y) + 200)
        self.plot.set_ydata(y)
        self.plot.set_xdata(x)
        self.canvas.draw()
        self.canvas.flush_events()
        
        

class FurnaceContent(QWidget):
    """
    stacked page which represents furnace's state

    setting_popup = detail temperature and time setting popup page

    number = furnace number
    sock = socket (used when communicate with server)
    dbconn = database conncection

    layout = main layout of FuranceContent
    """
    def __init__(self, furnace_number:int, sock, dbconn):
        super().__init__()
        self.setting_popup = SubWindow()
        self.number = furnace_number
        self.sock = sock
        self.dbconn = dbconn
        
        self.heattime_list = []
        self.staytime_list = []
        self.temp_list = []
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()

        self.detail_disable = []
        self.detail_able = []
        self.base_disable = []
        self.base_able = []

        #sensor area : sensor data (temp1~6, flow, press)
        self.sensor_area = SensorPlot()

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

        set_base_button = button.Base_Button(parameter.decision_str)

        base_area.addWidget(material_opt)
        base_area.addWidget(process_opt)
        base_area.addWidget(amount_opt)
        base_area.addWidget(set_base_button)

        #detail element setting
        detail_area = QVBoxLayout()
        buttons_in_detail_area = QHBoxLayout()

        set_temper_time_button = QPushButton('시간/온도 상세설정')
        set_temper_time_button.clicked.connect(self.set_detail_temp_time_click)

        gas_opt = QComboBox(self)
        gas_opt.addItem('gas1')
        gas_opt.addItem('gas2')
        gas_opt.addItem('gas3')

        set_detail_button = button.Detail_Button(parameter.decision_str)
        end_process_button = QPushButton('공정중지')
        end_process_button.setStyleSheet("background-color: red")

        detail_area.addWidget(set_temper_time_button)
        detail_area.addWidget(gas_opt)

        buttons_in_detail_area.addWidget(set_detail_button) 
        buttons_in_detail_area.addWidget(end_process_button)

        detail_area.addLayout(buttons_in_detail_area)      

        
        self.base_able.append(material_opt)
        self.base_able.append(process_opt)
        self.base_able.append(amount_opt)
        self.base_disable.append(set_temper_time_button)
        self.base_disable.append(gas_opt)
        self.base_disable.append(set_detail_button)
        self.base_disable.append(end_process_button)

        self.detail_able.append(set_base_button)
        self.detail_able.append(gas_opt)
        self.detail_able.append(set_temper_time_button)
        
        #test functions 
        base_area.itemAt(3).widget().set_change_widget_list(self.base_disable, self.base_able)
        detail_area.itemAt(2).itemAt(0).widget().set_change_widget_list(self.detail_disable, self.detail_able)
        #until this line

        base_area.itemAt(3).widget().clicked.connect(lambda:set_base_button.button_click(str(material_opt.currentText()), str(process_opt.currentText()), str(amount_opt.currentText()), self.sock))
        detail_area.itemAt(2).itemAt(0).widget().clicked.connect(lambda:set_detail_button.button_click(str(gas_opt.currentText()), self.temp_list, self.heattime_list, self.staytime_list,self.sock))
        detail_area.itemAt(2).itemAt(1).widget().clicked.connect(lambda:button.stop_button_click(self.sock))

        self.right_area.addLayout(base_area,2)
        self.right_area.addLayout(detail_area,2)

        #concat
        self.layout.addWidget(self.sensor_area,3)
        self.layout.addLayout(self.right_area, 1)

        #초기 실행시 세부설정을 불가능하게
        for widget in self.base_disable:
            widget.setEnabled(False)

        self.setLayout(self.layout)


    def init_data(self, process_setting, sensors):
        """
        process_setting's format =  [process_id, material, amount, process, count, temp_list, heattime, staytime, gas, output]
        """
        process_id, material, amount, process, count = process_setting[:5]
        temp_list, heattime_list, staytime_list = process_setting[5:5+count], process_setting[15:15+count], process_setting[25:25+count]
        gas = process_setting[-2]

        number = process_id[:2]
        print('furnace content 312 : ' + number)

        temp_list = list(map(str, temp_list))
        heattime_list = list(map(str, heattime_list))
        staytime_list = list(map(str, staytime_list))
        temp = ' '.join(temp_list)
        heattime = ' '.join(heattime_list)
        staytime = ' '.join(staytime_list)

        #setting qcombobox text to current process's options
        base_area = self.right_area.itemAt(0)
        detail_area = self.right_area.itemAt(1)

        material_opt = base_area.itemAt(0).widget()
        process_opt = base_area.itemAt(1).widget()
        amount_opt = base_area.itemAt(2).widget()
        gas_opt = detail_area.itemAt(1).widget()

        index = material_opt.findText(material, QtCore.Qt.MatchFixedString)
        material_opt.setCurrentIndex(index)
        index = process_opt.findText(process, QtCore.Qt.MatchFixedString)
        process_opt.setCurrentIndex(index)
        index = amount_opt.findText(str(amount), QtCore.Qt.MatchFixedString)
        amount_opt.setCurrentIndex(index)
        index = gas_opt.findText(gas, QtCore.Qt.MatchFixedString)
        gas_opt.setCurrentIndex(index)
        #qcombobox setting finish


        #send to server to notice about ongoing process
        base_msg = material + ' ' + process + ' ' + str(amount)
        detail_msg = str(count) + ' ' + temp + ' ' + heattime + ' ' + staytime + ' ' + gas
        init_msg = 'init ' + number + ' ' + base_msg + ' ' + detail_msg

        init_byte = init_msg.encode()
        self.sock.sendall(init_byte)
        #confirm msg from server
        _ = self.sock.recv(1024)

        #init plot with sensor datas
        self.sensor_area.init_data(sensors)

        for widget in self.base_able:
            widget.setEnabled(False)

        for widget in self.detail_able:
            widget.setEnabled(False)
        
        btn_base_modi = self.right_area.itemAt(0).itemAt(3).widget()
        btn_detail_modi = self.right_area.itemAt(1).itemAt(2).itemAt(0).widget()
        btn_end_process = self.right_area.itemAt(1).itemAt(2).itemAt(1).widget()
        btn_detail_modi.setEnabled(True)
        btn_end_process.setEnabled(True)
        btn_base_modi.custom_toggle()
        btn_detail_modi.custom_toggle()
        


    def set_detail_temp_time_click(self):
        win = self.setting_popup
        r = win.showModel()

        if r:
            count = win.setting_area.count()
            heattime_list, staytime_list, temp_list = [], [], []
            for i in range(count):
                temp_list.append(win.setting_area.itemAt(i).itemAt(0).widget().text())
                heattime_list.append(win.setting_area.itemAt(i).itemAt(1).widget().text())
                staytime_list.append(win.setting_area.itemAt(i).itemAt(2).widget().text())

            self.heattime_list = heattime_list
            self.staytime_list = staytime_list
            self.temp_list = temp_list
            


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

        #total popup page layout
        self.layout = QHBoxLayout()

        #time and temper graph area
        self.graph_area = QVBoxLayout()
        self.setting_graph = SettingPlot()
        btn_graph_renew = QPushButton("설정 미리보기")
        btn_graph_renew.clicked.connect(self.Renewbutton_click)
        self.graph_area.addWidget(self.setting_graph, 9)
        self.graph_area.addWidget(btn_graph_renew, 1)
        

        #area where input time, temper and button placed
        self.right_area = QVBoxLayout()
        #consist of ok button and cancel button
        self.OK_CAN = QHBoxLayout()
        #area where input time and temper
        self.setting_area = QVBoxLayout()
        self.button_area = QVBoxLayout()


        btnOK = QPushButton("확인")
        btnOK.clicked.connect(self.OKbutton_click)
        btnCancel = QPushButton("취소")
        btnCancel.clicked.connect(self.Cancelbutton_click)
        btnAdd = QPushButton("추가")
        btnAdd.clicked.connect(self.Addbutton_click)

        self.setting_area.addLayout(self.setting_row())
        self.OK_CAN.addWidget(btnOK, 1)
        self.OK_CAN.addWidget(btnCancel, 1)
        self.button_area.addWidget(btnAdd)
        self.button_area.addLayout(self.OK_CAN)

        self.right_area.addLayout(self.setting_area, 5)
        self.right_area.addLayout(self.button_area, 3)

        self.layout.addLayout(self.graph_area, 7)
        self.layout.addLayout(self.right_area, 3)

        self.setLayout(self.layout)

    def setting_row(self):
        row = QHBoxLayout()  
        number = self.setting_area.count()
        heattime_input = QLineEdit(self)
        staytime_input = QLineEdit(self)
        temp_input = QLineEdit(self)

        btnDel = QPushButton('삭제')
        row.addWidget(temp_input, 3)
        row.addWidget(heattime_input, 3)
        row.addWidget(staytime_input, 3)
        row.addWidget(btnDel, 1)
        row.itemAt(3).widget().clicked.connect(lambda:self.Delbutton_click(row))

        return row


    def Addbutton_click(self):
        if self.setting_area.count() < 10:
            self.setting_area.addLayout(self.setting_row())

    ##before delete layout, you must delete all widget in layout
    def Delbutton_click(self, widget):
        count = self.setting_area.count()

        if count >= 2:
            for i in reversed(range(widget.count())):
                widget.itemAt(i).widget().setParent(None)
            self.setting_area.removeItem(widget)

    def Renewbutton_click(self):
        time_list = [0]
        temp_list = [0]
        
        for i in range(self.setting_area.count()):
            target = self.setting_area.itemAt(i)
            temp_list.append(int(target.itemAt(0).widget().text()))
            temp_list.append(int(target.itemAt(0).widget().text()))
            time_list.append(time_list[-1] + int(target.itemAt(1).widget().text()))
            time_list.append(time_list[-1] + int(target.itemAt(2).widget().text()))

        self.setting_graph.update(time_list, temp_list)
        


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