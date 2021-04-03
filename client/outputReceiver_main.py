from PyQt5.QtWidgets import *
import sys

import output_receiver
import RecvOutputWindow
import utils

#'03_2104031748/material3/process3/300/1/300/5/5/gas2' 참고용
if __name__ == "__main__":
    process_option_list = utils.change_str_to_process_option(sys.argv[1])
    app = QApplication(sys.argv)

    form = RecvOutputWindow.RecvOutputWindow(process_option_list)
    form.show()

    sys.exit(app.exec_())