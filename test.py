import pymysql
import parameter
import sys
import time

dbconn = pymysql.connect(host=parameter.host, user = parameter.user, passwd = parameter.password, db = parameter.db, charset = parameter.charset)
dbcur = dbconn.cursor()



dbconn.commit()
sql = """select id from process"""

dbcur.execute(sql)
result = dbcur.fetchall()
print(result[0][0])




    