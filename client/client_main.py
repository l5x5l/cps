from PyQt5.QtWidgets import *
import sys
import threading
import pymysql

import client
import output_receiver
import homepage
import parameter
import thread


if __name__ == "__main__":
    C = client.Client(parameter.host, parameter.port)
    C.connect()
    O = output_receiver.OutputReceiver(parameter.host, parameter.port)
    O.connect()
    dbconn = pymysql.connect(host=parameter.host, user = parameter.user, password=parameter.password, database=parameter.db, charset = parameter.charset)
    app = QApplication(sys.argv)

    form = homepage.HomePage(C, O, dbconn)
    form.show()

    sys.exit(app.exec_())