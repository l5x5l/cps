import random
import parameter

#이건 서버에서 현재 작동중인 열처리로를 확인하기 위해 사용
class Datas:
    def __init__(self, total_furncae:int):
        self.datas = []
        self.total = total_furncae
        for i in range(self.total):
            self.datas.append({'state':'-', 'process':'-'})
    

    def close_furnace_data(self, number:int):
        index = number - 1
        self.datas[index]['state'] = '-'
        self.datas[index]['process'] = '-'


    # 오직 테스트용으로만 사용, 그 이외의 용도로는 사용을 금함
    def for_test(self):
        test_number = []
        for i in range(5):
            test_number.append(random.randrange(0, parameter.total_furnace))

        for test in test_number:
            self.datas[test]['state'] = 'on'
            self.datas[test]['process'] = 'test_process'


    def on_furnace_data(self, number:int):
        index = number - 1
        self.datas[index]['state'] = 'on'
        

    def working_furnace_data(self, number:int, process_id:str):
        index = number - 1
        self.datas[index]['state'] = 'working'
        self.datas[index]['process']  = process_id


    def state_furnace(self):
        output_str = ""
        for i in range(self.total):
            output_str += str(i+1)
            if self.datas[i]['state'] == '-':
                output_str += 'XX\n'
            elif self.datas[i]['state'] == 'on':
                output_str += "On\n"
            elif self.datas[i]['state'] == 'working':
                output_str += "work\n"
            else:
                output_str += "??\n"
        
        return output_str

    
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


#이건 클라이언트에서 센서값을 실시간으로 담아두기 위해 사용
class Sensors:
    def __init__(self, total_furnace:int):
        self.total_furnace = total_furnace
        self.sensors = []
        for i in range(total_furnace):
            self.sensors.append([])
        

    def set_first(self, sensors:list, index:int):
        self.sensors[index] = sensors
        

    def renew(self, sensor):
        for i in range(self.total_furnace):
            if len(self.sensors[i]) >= 30:
                self.sensors[i][:-1] = self.sensors[i][1:]
                self.sensors[i][-1] = sensor[i]
            else:
                self.sensors[i].append(sensor[i])

    
    def get_sensor(self, number):
        index = number - 1
        return self.sensors[index]