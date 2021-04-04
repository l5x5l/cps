import server
import parameter

serv = server.Server(parameter.host, parameter.port, parameter.total_furnace, parameter.maximum_client)
while True:
    conn_sock, confirm_msg = serv.connect()
    serv.start_thread(conn_sock, confirm_msg)
    