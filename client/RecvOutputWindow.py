from PyQt5.QtWidgets import *
import output_receiver
import plot

class RecvOutputWindow(QWidget):
    """
    
    """
    def __init__(self, process_option_list:list):
        super().__init__()
        self.initUI()
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

        self.settingPlot = plot.SettingPlot()

        self.initUI()

    def initUI(self):
        self.mainlayout = QVBoxLayout()

        process_id_text = QLabel(f"""평가 대상 공정 : {self.process_option["id"]}""")

        process_base_text = QHBoxLayout()
        process_meterial_text = QLabel(f"""재료 : {self.process_option["meterial"]}""")
        process_manufacture_text = QLabel(f"""공정방식 : {self.process_option["manufacture"]}""")
        process_inputAmount_text = QLabel(f"""투입량 : {self.process_option["inputAmount"]}""")
        process_base_text.addWidget(process_meterial_text)
        process_base_text.addWidget(process_manufacture_text)
        process_base_text.addWidget(process_inputAmount_text)

        

        self.setLayout(self.mainlayout)
        self.setWindowTitle("output receiver")