import sys
import homepage
import parameter
import thread
import threading
import client
import pymysql

from PyQt5.QtWidgets import *

if __name__ == "__main__":
    C = client.Client(parameter.host, parameter.port)
    C.connect()
    dbconn = pymysql.connect(host=parameter.host, user = parameter.user, password=parameter.password, database=parameter.db, charset = parameter.charset)
    app = QApplication(sys.argv)

    form = homepage.HomePage(C, dbconn)
    form.show()

    #dbconn.close()
    sys.exit(app.exec_())