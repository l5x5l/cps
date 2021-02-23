import sys
import homepage
import parameter
import thread
import threading
import client
from PyQt5.QtWidgets import *

if __name__ == "__main__":
    C = client.Client(parameter.host, parameter.port)
    C.connect()
    app = QApplication(sys.argv)

    form = homepage.HomePage(C.sock)
    form.show()

    sys.exit(app.exec_())