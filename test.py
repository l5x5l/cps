import pymysql
import parameter
import sys
import time
import datetime

test_time = datetime.datetime.now().replace(microsecond=0)
test_str = "03/30/21 13:55:26"

print(int((datetime.datetime.now().replace(microsecond=0) - datetime.datetime.strptime(test_str, "%m/%d/%y %H:%M:%S")).total_seconds()))