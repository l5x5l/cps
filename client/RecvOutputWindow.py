from PyQt5.QtWidgets import *
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

        self.settingPlot = plot.SettingPlot2()

        self.initUI()

    def initUI(self):
        self.setStyleSheet('background-color:white')
        self.mainlayout = QVBoxLayout()
        self.processArea = QVBoxLayout()
        self.recvOutputArea = QVBoxLayout()
        
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
        
        self.processArea.addWidget(text)
        self.processArea.addWidget(process_id_text)
        self.processArea.addLayout(process_base_text)
        self.processArea.addWidget(self.settingPlot)

        

        self.setLayout(self.processArea)
        self.setWindowTitle("output receiver")

