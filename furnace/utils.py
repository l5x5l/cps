import datetime

def get_elapsed_time(start_time):
    """
    공정 소요 시간을 계산하는 함수\n
    start_time(str or datetime.datetime) : "%m/%d/%y %H:%M:%S"형식을 가지고 있으며, 본 함수를 실행할 때의 now time에서 start_time을 뺀 시간을 초단위로 리턴\n
    return type : int
    """
    if type(start_time) is str:
        output = int((datetime.datetime.now().replace(microsecond=0) - datetime.datetime.strptime(start_time, "%m/%d/%y %H:%M:%S")).total_seconds())
    else:
        output = int((datetime.datetime.now().replace(microsecond=0) - start_time).total_seconds())

    return output