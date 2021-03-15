host='127.0.0.1' 
user='root'
password='13130132'
db = 'cps'
charset='utf8'

total_furnace = 8
port = 3050
time_interval = 2
maximum_client = 10

height = 500
width = 1000

#button에 넣을 문자열들
decision_str = "결정"
restart_str = "재시작"
modify_str = "수정"
add_str = '추가'
del_str = '삭제'
confirm_str = '확인'
cancel_str = '취소'
end_process_str = '공정중지'
set_temper_time_str = '시간/온도 세부설정'
show_temper_time_str = '세부설정 미리보기'

success_str = 'success'
error_str = 'error'

test_sql = """select id from process"""
sql = """select id from process where output is null"""

json_path = '.\\json\\combobox.json'