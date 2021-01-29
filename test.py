import pymysql
import parameter
import sys
import time

dbconn = pymysql.connect(host=parameter.host, user = parameter.user, passwd = parameter.password, db = parameter.db, charset = parameter.charset)
dbcur = dbconn.cursor()


while  True:
    dbconn.commit()
    sql = """select id from process"""
    #sql = """select touch ,temp1, temp2, temp3, temp4, temp5, temp6, flow, press from furnace1 where id = '01_2101282006'"""
    dbcur.execute(sql)
    result = list(dbcur.fetchall())
    print(len(result))
    processes = []
    time.sleep(parameter.time_interval)
'''
for i in range(parameter.total_furnace):
    processes.append(None)

for elem in result:
    number = int(elem[0][:2])
    #print(elem)
    processes[number - 1] = elem[0]

for process in processes:
    if process is None:
        print('process is not exist')
        continue

    temp = ""
    number = int(process[:2])
    print('furnace' + str(number) + '---------------')
    sql = """select * from furnace""" + str(number) + """ where id = '""" + process + """' order by current desc limit 30"""
    dbcur.execute(sql)
    result = list(dbcur.fetchall())
    result.reverse()
    print(result[-1])
'''
'''
    for a in result:
        for b in a:
            temp += str(b)
            temp += ' '
        temp += '/'


    steps = temp.split('/')
    steps.pop()
    for step in steps:
        if step == '':
            print('last')
        else:
            print(step)
    
'''




    