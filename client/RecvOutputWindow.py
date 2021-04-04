from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication 
import output_receiver
import plot
import sys
import utils

class RecvOutputWindow(QWidget):
    """
    
    """
    def __init__(self, process_option_str:str):
        super().__init__()

        process_option_list = utils.change_str_to_process_option(process_option_str)
        self.process_option = {}
        self.process_option["id"] = process_option_list[0]
        self.process_option["meterial"] = process_option_list[1]
        self.process_option["manufacture"] = process_option_list[2]
        self.process_option["inputAmount"] = process_option_list[3]
        self.process_option["count"] = process_option_list[4]
        self.process_option["tempList"] = process_option_list[5]
        self.process_option["heattimeList"] = process_option_list[6]
        self.process_option["staytimeList"] = process_option_list[7]
        self.process_option["gas"] = process_option_list[8]

        self.satisfaction = None
        self.satisfaction_radio_list = []
        self.errorRate = None
        self.errorRate_radio_list = []

        self.settingPlot = plot.SettingPlot()

        self.initUI()

    def initUI(self):
        self.setStyleSheet('background-color:white')
        self.mainlayout = QVBoxLayout()
        self.processArea = QVBoxLayout()
        self.recvOutputArea = QVBoxLayout()
        
        #self.process_area의 구성 widget들 선언
        text = QLabel("공정 정상 종료 이후 평가")
        process_id_text = QLabel(f"""평가 대상 공정 : {self.process_option["id"]}""")

        process_base_text = QHBoxLayout()
        process_meterial_text = QLabel(f"""재료 : {self.process_option["meterial"]}""")
        process_manufacture_text = QLabel(f"""공정방식 : {self.process_option["manufacture"]}""")
        process_inputAmount_text = QLabel(f"""투입량 : {self.process_option["inputAmount"]}""")
        process_base_text.addWidget(process_meterial_text)
        process_base_text.addWidget(process_manufacture_text)
        process_base_text.addWidget(process_inputAmount_text)

        plot_temp, plot_time = utils.make_plot_data(self.process_option["count"], self.process_option["tempList"], self.process_option["heattimeList"], self.process_option["staytimeList"])
        self.settingPlot.update(plot_time, plot_temp)
        settingPlot_Groupbox = QGroupBox("공정 세부 과정(온도/시간)")
        settingPlot_layout = QVBoxLayout()
        settingPlot_layout.addWidget(self.settingPlot)
        settingPlot_Groupbox.setLayout(settingPlot_layout)

        #self.processArea에 widget들을 add
        self.processArea.addWidget(text)
        self.processArea.addWidget(process_id_text)
        self.processArea.addLayout(process_base_text)
        self.processArea.addWidget(settingPlot_Groupbox)

        #self.recvOutputArea의 구성 widget들 선언
        self.satisfactionGroupBox = QGroupBox("공정에 대한 전반적인 결과 만족도")
        hbox = QHBoxLayout()
        self.satisfaction_radio_list.append(QRadioButton("불만족"))
        self.satisfaction_radio_list.append(QRadioButton("보통"))
        self.satisfaction_radio_list[-1].setChecked(True)
        self.satisfaction_radio_list.append(QRadioButton("만족"))
        for i in range(len(self.satisfaction_radio_list)):
            self.satisfaction_radio_list[i].clicked.connect(self.satisfaction_radio_clicked)
            hbox.addWidget(self.satisfaction_radio_list[i])
        self.satisfactionGroupBox.setLayout(hbox)

        self.errorRateGroupBox = QGroupBox("공정 결과물의 손상률")
        hbox2 = QHBoxLayout()
        self.errorRate_radio_list.append(QRadioButton("0.1% 미만"))
        self.errorRate_radio_list.append(QRadioButton("0.1% ~ 0.3%"))
        self.errorRate_radio_list.append(QRadioButton("0.3% ~ 0.5%"))
        self.errorRate_radio_list[-1].setChecked(True)
        self.errorRate_radio_list.append(QRadioButton("0.5% ~ 0.7%"))
        self.errorRate_radio_list.append(QRadioButton("0.7% ~ 0.9%"))
        self.errorRate_radio_list.append(QRadioButton("0.9% 초과"))
        for i in range(len(self.errorRate_radio_list)):
            self.errorRate_radio_list[i].clicked.connect(self.errorRate_radio_clicked)
            hbox2.addWidget(self.errorRate_radio_list[i])
        self.errorRateGroupBox.setLayout(hbox2)

        submitButton = QPushButton("제출")
        submitButton.clicked.connect(self.confirmButtonClick)

        #self.recvOutputArea에 widget을 add
        self.recvOutputArea.addWidget(self.satisfactionGroupBox)
        self.recvOutputArea.addWidget(self.errorRateGroupBox)
        self.recvOutputArea.addWidget(submitButton)

        #self.mainLayout에 layout들을 add
        self.mainlayout.addLayout(self.processArea)
        self.mainlayout.addLayout(self.recvOutputArea)

        self.setLayout(self.mainlayout)
        self.setWindowTitle("output receiver")

    def satisfaction_radio_clicked(self):
        for satisfaction in self.satisfaction_radio_list:
            if satisfaction.isChecked():
                self.satisfaction = satisfaction.text()
        
    def errorRate_radio_clicked(self):
        for errorRate_radio in self.errorRate_radio_list:
            if errorRate_radio.isChecked():
                self.errorRate = errorRate_radio.text()

    def confirmButtonClick(self):
        print(self.process_option)
        print(self.satisfaction, self.errorRate)
        QCoreApplication.instance().quit()
