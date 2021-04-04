from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pyqtgraph import PlotWidget, mkPen, ViewBox, InfiniteLine
import numpy as np


## 실시간 센서값 그래프
class SensorPlotCanvas(FigureCanvas):
    """
    SensorArea의 그래프 부분
    group of plots which represent sensor value in realtime
    """
    def __init__(self, parent = None, width = 5, height = 4, dpi = 100):
        self.fig = Figure()

        self.temp1 = self.fig.add_subplot(421, xlim=(0, 50), ylim=(0, 1500))
        self.temp2 = self.fig.add_subplot(422, xlim=(0, 50), ylim=(0, 1500))
        self.temp3 = self.fig.add_subplot(423, xlim=(0, 50), ylim=(0, 1500))
        self.temp4 = self.fig.add_subplot(424, xlim=(0, 50), ylim=(0, 1500))
        self.temp5 = self.fig.add_subplot(425, xlim=(0, 50), ylim=(0, 1500))
        self.temp6 = self.fig.add_subplot(426, xlim=(0, 50), ylim=(0, 1500))
        self.flow = self.fig.add_subplot(427, xlim=(0, 50), ylim=(0, 100))
        self.press = self.fig.add_subplot(428, xlim=(0, 50), ylim=(0, 100))

        self.compute_initial_figure()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.draw()
        self.flush_events()

    def compute_initial_figure(self):
        pass

class SensorArea(QWidget):
    """
    센서값을 사용하는 부분

    base_box : main layout of SensorPlot
    left_area : 센서값 8개를 그래프로 표시하는 부분
    middle_area : 열처리로 이미지와 센서값을 수치상으로 표현하는 부분으로 구성
    """
    def __init__(self):
        QMainWindow.__init__(self)

        self.base_box = QHBoxLayout()

        self.left_area = QVBoxLayout()
        self.canvas = SensorPlotCanvas(self, width=10, height=8, dpi=100)
        self.left_area.addWidget(self.canvas)

        #middle area에도 센서값을 표시하는 구역이 존재하므로 통합
        self.middle_area = QVBoxLayout()
        state_text = QLabel()
        furnace_img = QLabel()
        furnace_img.setPixmap(QPixmap('.\\images\\furnace.png'))

        self.sensor_table = QVBoxLayout()
        sensorname_list = ["온도1", "온도2", "온도3", "온도4", "온도5", "온도6", "유량", "압력"]
        for sensorname in sensorname_list:
            temp = QHBoxLayout()
            namePart = QLabel(sensorname)
            sensorValuePart = QLabel()

            temp.addWidget(namePart)
            temp.addWidget(sensorValuePart)

            self.sensor_table.addLayout(temp)

        self.middle_area.addWidget(state_text, 1)
        self.middle_area.addWidget(furnace_img, 1)
        self.middle_area.addLayout(self.sensor_table, 8)


        self.base_box.addLayout(self.left_area, 2)
        self.base_box.addLayout(self.middle_area, 1)

        self.setLayout(self.base_box)

        self.subplot_list = [self.canvas.temp1, self.canvas.temp2, self.canvas.temp3, self.canvas.temp4, self.canvas.temp5, self.canvas.temp6,self.canvas.flow, self.canvas.press]
        self.line = ["", "", "", "", "", "", "", ""]    #각 센서당 센서값들을 저장, 비어있으면 ""로 표기
        
        for i in range(len(self.subplot_list)):              
            x = np.arange(50)
            y = np.ones(50, dtype=np.float)*np.nan
            self.line[i], = self.subplot_list[i].plot(x, y, animated=False)
    
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


    def update(self, sensorData):
        """
        열처리로 페이지에서 센서값을 반영해 plot과 텍스트 업데이트

        sensorData : sensor data -> [current, id, touch, temp1~6, flow, press]
        type of datas elemnt without touch : int
        """

        for index, _ in enumerate(self.line):
            y = int(sensorData[index + 3])
            sensorValuePart = self.sensor_table.itemAt(index).itemAt(1).widget()

            valueAndUnitText = str(y) + (' C(임시)' if index < 6 else ' (임시)')
            sensorValuePart.setText(valueAndUnitText)

            old_y = self.line[index].get_ydata()
            new_y = np.r_[old_y[1:], y]
            self.line[index].set_ydata(new_y)

        self.canvas.draw()
        self.canvas.flush_events()

    def clear(self):
        """
        clear graph of furance
        """
        y = np.ones(50, dtype=np.float)*np.nan
        for index, _ in enumerate(self.line):
            self.line[index].set_ydata(y)
        self.canvas.draw()
        self.canvas.flush_events()


## 공정 세부설정 (온도/시간)을 그래프로 표현
class SettingPlotCanvas(FigureCanvas):
    """
    plot which represents detail temperature and time setting 
    """
    def __init__(self, parent=None):
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
        self.canvas = SettingPlotCanvas(self)
        self.plot, = self.canvas.ax.plot([0],[0], animated=False)
        self.base_box.addWidget(self.canvas)
        self.setLayout(self.base_box)
        self.canvas.draw()

    def update(self, x, y, elapsed_time = None):
        # if elapsed_time:
        #     self.canvas.ax.axvspan(0, elapsed_time, color="red")
        self.canvas.ax.set_xlim(0, x[-1])
        self.canvas.ax.set_ylim(0, max(y) + 200)
        self.plot.set_ydata(y)
        self.plot.set_xdata(x)
        self.canvas.draw()
        self.canvas.flush_events()
        
    def clear(self):
        self.canvas.ax.clear()


class SettingPlot2(PlotWidget):
    def __init__(self):
        super().__init__()
        #self.enableAutoRange(axis='x')
        self.setMouseEnabled(y=False, x = False)
        self.setBackground('w')
        # self.showGrid(x = True, alpha = 0.3)
        self.pen = mkPen(width=2, color=(200, 200, 255))

    def update(self, x, y, elapse_time=None):
        self.clear()
        if elapse_time:
            vertical_line = InfiniteLine(pos=elapse_time, angle=90, pen='r')
            self.addItem(vertical_line)
        self.plot(x, y, pen=self.pen)

    def clear(self):
        self.clear()
# import sys
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     s = SettingPlot2()
#     sys.exit(app.exec_())