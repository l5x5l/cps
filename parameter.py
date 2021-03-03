host='165.246.44.133' 
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

decision_str = "결정"
modify_str = "수정"

success_str = 'success'
error_str = 'error'

test_sql = """select id from process"""
sql = """select id from process where output is null"""