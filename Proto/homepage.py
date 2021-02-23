import parameter
import furnace_content
import sys
import client
import button
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Select(QWidget):
    def __init__(self, stk_w):
        super().__init__()
        self.stk_w = stk_w
        self.initUI()
    
    def initUI(self):
        self.layout = QHBoxLayout()
        #image area
        self.image_area = QWidget()
        self.image_area.setStyleSheet('background-color:#87CEFA;')

        #furnace area, where furnace button placed
        self.furnace_area = QGridLayout()
        furnace_buttons = []
        for i in range(parameter.total_furnace): 
            furnace_buttons.append(QPushButton('furnace' + str(i + 1)))
            furnace_buttons[i].resize((parameter.height-100)//4, (parameter.height-100)//4)
            furnace_buttons[i].setMaximumHeight((parameter.height-100)//4)
            furnace_buttons[i].clicked.connect(lambda checked, index=i:button.furnace_button_click(self.stk_w, index+1))
            #(lambda checked, index=i:button.furnace_button_click(self.stk_w, index+1))
            #(lambda:button.furnace_button_click(self.stk_w, i+1))
            self.furnace_area.addWidget(furnace_buttons[i], i // 2, i % 2)  

        #except setting area, which content is plot or furnace select
        self.layout.addWidget(self.image_area)
        self.layout.addLayout(self.furnace_area)
        self.setLayout(self.layout)

class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()
        self.dyn_content = QStackedWidget()

        #setting area, where setting button, back button and icon image placed
        self.setting_area = QVBoxLayout()
        icon = QWidget()
        icon.setStyleSheet('background-color:#7FFFD4;')
        set_button = QPushButton('setting')
        back_button = QPushButton('back')
        back_button.clicked.connect(lambda:button.back_button_click(self.dyn_content))

        self.setting_area.addWidget(icon)
        self.setting_area.addWidget(set_button)
        self.setting_area.addWidget(back_button)

        #changeable area
        self.content_area = Select(self.dyn_content)
        self.dyn_content.addWidget(self.content_area)
        self.furnace_list = []
        for i in range(parameter.total_furnace):
            self.furnace_list.append(furnace_content.FurnaceContent(i+1, None))
            self.dyn_content.addWidget(self.furnace_list[i])


        #settting area | image area | furnace area
        self.layout.addLayout(self.setting_area, 1)
        self.layout.addWidget(self.dyn_content, 10)

        self.setLayout(self.layout)
        self.setWindowTitle('CPS ProtoType')
        self.setGeometry(0, 0, parameter.width, parameter.height)

def back_button_click(stk_w):
    stk_w.setCurrentIndex(0)


def furnace_button_click(stk_w, index:int):
    stk_w.setCurrentIndex(index)

if __name__ == "__main__":
    #C = client.Client(parameter.host, parameter.port)
    #C.connect()

    app = QApplication(sys.argv)
    form = HomePage()
    form.show()

    sys.exit(app.exec_())