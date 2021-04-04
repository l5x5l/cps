from PyQt5.QtWidgets import *
import output_receiver

class RecvOutputWindow(QWidget):
    """
    
    """
    def __init__(self, output_receiver:output_receiver.OutputReceiver):
        super().__init__()
        self.output_receiver_instance = output_receiver
        self.initUI()

    def initUI(self):
        self.mainlayout = QVBoxLayout()


        self.setLayout(self.mainlayout)
        self.setWindowTitle("output receiver")