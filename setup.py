import pymysql
import parameter
import sys

#본 코드를 실행하기 전 cps라는 이름을 가진 database를 생성해야 한다.
#-> sql client에서 create database cps사용
dbconn = pymysql.connect(host=parameter.host, user = parameter.user, passwd = parameter.password, db = parameter.db, charset = parameter.charset)
dbcur = dbconn.cursor()
total_furnace = parameter.total_furnace

try:
    total_furnace = int(total_furnace)
except:
    print('[setup] wrong input, argument must be integer')
    exit()



sql =  """CREATE TABLE Process(id CHAR(13) PRIMARY KEY, material VARCHAR(20), amount INT, manufacture VARCHAR(20), temperature INT, time INT, gas VARCHAR(20), output INT)"""
dbcur.execute(sql)

for i in range(total_furnace):
    number = i + 1
    sql = """CREATE TABLE Furnace%s(current CHAR(6), id CHAR(13), touch VARCHAR(10), temp1 INT, temp2 INT, temp3 INT, temp4 INT, temp5 INT, temp6 INT, flow INT, press INT, PRIMARY KEY(current, id))"""
    val = (number)
    dbcur.execute(sql, val)

#touch, temp1, temp2, temp3, temp4, temp5, temp6, flow, press