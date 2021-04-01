import datetime
import time
import utils
import pymysql
import parameter

# start_time = datetime.datetime.now().replace(microsecond=0)
# start_time_str = start_time.strftime("%m/%d/%y %H:%M:%S")

# dbconn = pymysql.connect(host=parameter.host, user = parameter.user, password=parameter.password, database=parameter.db, charset = parameter.charset)
# dbcur = dbconn.cursor()

# sql = f"""select starttime from process where output = 1"""
# dbcur.execute(sql)
# result = list(dbcur.fetchall()[0])
# if type(start_time) is str:
#     print("here")
#     output = int((datetime.datetime.now().replace(microsecond=0) - datetime.datetime.strptime(start_time, "%m/%d/%y %H:%M:%S")).total_seconds())
# else:
#     print("nope")
#     output = int((datetime.datetime.now().replace(microsecond=0) - start_time).total_seconds())

# print(result)
test = None
if test:
    print("line")