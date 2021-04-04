from PyQt5.QtWidgets import *
import sys

import output_receiver
import RecvOutputWindow

## 단순히 UI만을 시험하기 위한 예제들
#'03_2104031748/material3/process3/300/1/300/5/5/gas2'
#'04_2104032022/material2/process3/300/1/150/15/15/gas1'
#'07_2104032021/material2/process1/500/3/150-300-500/15-15-15/15-15-15/gas2'
if __name__ == "__main__":
    app = QApplication(sys.argv)

    form = RecvOutputWindow.RecvOutputWindow(sys.argv[1])
    #단순히 UI만을 테스트하기 위한 임시값
    #form = RecvOutputWindow.RecvOutputWindow('07_2104032021/material2/process1/500/3/150-300-500/15-15-15/15-15-15/gas2')
    form.show()

    sys.exit(app.exec_())