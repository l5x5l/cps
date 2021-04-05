import random

#이건 서버에서 현재 작동중인 열처리로를 확인하기 위해 사용
class Datas:
    def __init__(self, total_furncae:int):
        self.datas = []
        self.total = total_furncae
        for i in range(self.total):
            self.datas.append({'state':'-', 'process':'-', "start_time":'-'})
    

    def close_furnace_data(self, number:int):
        index = number - 1
        self.datas[index]['state'] = '-'
        self.datas[index]['process'] = '-'
        self.datas[index]['start_time'] = '-'

    def on_furnace_data(self, number:int):
        index = number - 1
        self.datas[index]['state'] = 'on'
        self.datas[index]['process'] = '-'
        self.datas[index]['start_time'] = '-'

    def working_furnace_data(self, number:int, process_id:str, start_time:str):
        index = number - 1
        self.datas[index]['state'] = 'working'
        self.datas[index]['process']  = process_id
        self.datas[index]['start_time'] = start_time
    
    def check_furnace(self, number:int, option:str):
        index = number - 1
        if option != 'start' and  option != 'fix' and option != 'end':
            return False, 'Error : wrong option'
        elif self.datas[index]['state'] == '-' and (option == 'end' or option == 'fix' or option == 'start'):
            return False, 'Error : already shut down'
        elif self.datas[index]['state'] == 'on' and (option == 'fix' or option == 'end'):
            return False, 'Error : this furnace is not working'
        elif self.datas[index]['state'] == 'work' and  option == 'start':
            return False, 'Error : this furnace is already working'
        else:
            return True, (str(number) + "'s option is " + option)

