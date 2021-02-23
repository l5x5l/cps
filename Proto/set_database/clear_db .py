import pymysql
import parameter
import sys

#본 코드를 실행하기 전 cps라는 이름을 가진 database를 생성해야 한다.
#-> sql client에서 create database cps사용
dbconn = pymysql.connect(host=parameter.host, user = parameter.user, passwd = parameter.password, db = parameter.db, charset = parameter.charset)
dbcur = dbconn.cursor()

sql =  """DROP TABLE process"""
dbcur.execute(sql)

sql =  """DROP TABLE furnace1"""
dbcur.execute(sql)

sql =  """DROP TABLE furnace2"""
dbcur.execute(sql)

sql =  """DROP TABLE furnace3"""
dbcur.execute(sql)

sql =  """DROP TABLE furnace4"""
dbcur.execute(sql)

sql =  """DROP TABLE furnace5"""
dbcur.execute(sql)

sql =  """DROP TABLE furnace6"""
dbcur.execute(sql)

sql =  """DROP TABLE furnace7"""
dbcur.execute(sql)

sql =  """DROP TABLE furnace8"""
dbcur.execute(sql)