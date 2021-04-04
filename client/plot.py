from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pyqtgraph import PlotWidget, mkPen, ViewBox, InfiniteLine
import numpy as np


class SensorPlot(PlotWidget):
    """
    센서값 하나에 대한 그래프
    """
    def __init__(self):
        super().__init__()
        self.setMouseEnabled(y=False)
        self.setBackground('w')
        self.pen = mkPen(width=2, color=(200, 200, 255))
        
    def update(self, current_time:list ,sensorData:list):
        self.clear()
        self.plot(current_time, sensorData, pen=self.pen)



class SensorArea(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)

        # 변수, sensorname은 센서의 이름, subplot_list는 SensorPlot widget을 모아둔 것
        # self.sensorValue_list와 self.time_list는 그래프를 그릴 때 y값, x값으로 사용된다
        self.sensorname_list = ["온도1", "온도2", "온도3", "온도4", "온도5", "온도6", "유량", "압력"]
        self.subplot_list = []
        self.sensorValue_list = [] 
        self.time_list = []

        for i in range(len(self.sensorname_list )):
            self.sensorValue_list.append([])

        # 레이아웃 부분, sensorArea_mainLayout은 본 클래스의 메인 레이아웃
        self.sensorArea_mainLayout = QHBoxLayout()

        self.sensorPlotArea = QVBoxLayout()
        self.middle_area = QVBoxLayout()

        #self.sensorPlotArea구성 요소 선언
        self.sensorPlots = QGridLayout()
        for i in range(len(self.sensorname_list)):
            sensorplot = SensorPlot()
            self.subplot_list.append(sensorplot)
            self.sensorPlots.addWidget(sensorplot, i//2, i%2)
        
        #self.sensorPlotArea구성
        self.sensorPlotArea.addLayout(self.sensorPlots)

        #self.sensorTableArea구성 요소 선언
        state_text = QLabel()
        furnace_img = QLabel()
        furnace_img.setPixmap(QPixmap('.\\images\\furnace.png'))
        self.sensorTable = QVBoxLayout()
        for sensorname in self.sensorname_list:
            temp = QHBoxLayout()
            namePart = QLabel(sensorname)
            sensorValuePart = QLabel()

            temp.addWidget(namePart)
            temp.addWidget(sensorValuePart)
            self.sensorTable.addLayout(temp)
        
        #self.sensorTableArea구성
        self.middle_area.addWidget(state_text)
        self.middle_area.addWidget(furnace_img)
        self.middle_area.addLayout(self.sensorTable)

        #main layout 구성
        self.sensorArea_mainLayout.addLayout(self.sensorPlotArea, 2)
        self.sensorArea_mainLayout.addLayout(self.middle_area, 1)

        self.setLayout(self.sensorArea_mainLayout)

    def init_data(self, datas):
        """
        원격제어 프로그램을 실행하기 전 이미 실행 중이던 공정에 대한 센서값을 읽어와 그래프에 반영하는 부분
        """
        temp1, temp2, temp3, temp4, temp5, temp6, flow, press = [], [], [], [], [], [], [], []

        for value in datas:
            self.time_list.append(int(value[0]))
            temp1.append(int(value[3]))
            temp2.append(int(value[4]))
            temp3.append(int(value[5]))
            temp4.append(int(value[6]))
            temp5.append(int(value[7]))
            temp6.append(int(value[8]))
            flow.append(int(value[9]))
            press.append(int(value[10]))

        
        self.sensorValue_list[0] = temp1
        self.sensorValue_list[1] = temp2
        self.sensorValue_list[2] = temp3
        self.sensorValue_list[3] = temp4
        self.sensorValue_list[4] = temp5
        self.sensorValue_list[5] = temp6
        self.sensorValue_list[6] = flow
        self.sensorValue_list[7] = press


        for index, _ in enumerate(self.subplot_list):
            self.subplot_list[index].update(self.time_list, self.sensorValue_list[index])

    def update(self, sensorData):
        """
        열처리로 페이지에서 센서값을 반영해 plot과 텍스트 업데이트

        sensorData : sensor data -> [current, id, touch, temp1~6, flow, press]\n
        touch를 제외한 나머지 센서값의 형식 : int\n
        touch는 str\n
        """
        self.time_list.append(int(sensorData[0]))
        for index, _ in enumerate(self.subplot_list):
            y = int(sensorData[index + 3])
            self.sensorValue_list[index].append(y)
            self.subplot_list[index].update(self.time_list, self.sensorValue_list[index])

            valueText = str(y) + (' C(임시)' if index < 6 else ' (임시)')
            self.sensorTable.itemAt(index).itemAt(1).widget().setText(valueText)
            


    def clear(self):
        self.time_list.clear()
        for i in range(len(self.sensorname_list)):
            self.sensorValue_list[i].clear()
        # 이미 그려진 그래프에 대한 초기화는 할 필요가 없다고 생각
            
        

class SettingPlot(PlotWidget):
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