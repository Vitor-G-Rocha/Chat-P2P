#coding=UTF-8

import socket
import _thread
import pymysql.cursors

def clientRecv(conn, addr, connection):
    while True:
        try:
            data = conn.recv(4096).decode() #Recebe usuário de quem conectou
            if(data):
                #print(data)
                try:
                    with connection.cursor() as cursor: #Atualiza quem conectou com o tracker pra online, e salva no BD o Ip e a porta do usuario
                        sqlQuery = "UPDATE `user` SET `status`=%s, `user_IP`=%s, `user_PORT`=%s WHERE `user_nome`=%s"
                        sqlQuery2 = "SELECT `nome_completo` FROM `user` WHERE `user_nome`=%s"
                        cursor.execute(sqlQuery, (1, addr[0], addr[1], data))
                        connection.commit()
                        result = cursor.execute(sqlQuery2, data)
                        resultSQL = [item['nome_completo'] for item in cursor.fetchall()]
                        print ('**************************************************************')
                        print("["+str(resultSQL[0])+"]"+" conectou!")
                        print("Ip: ["+str(addr[0])+"]"+" - "+"Porta: ["+str(addr[1])+"]")
                        print ('**************************************************************')
                except:
                    print("SQL ERROR!")
            else:
                print("["+str(resultSQL[0])+"]"+" desconectou!")
                conn.close()
                break
        except:
            print("Socket ERROR!")
            conn.close()
            break

def main():
    try: #Conexão com Banco
        connection = pymysql.connect(host='10.0.23.131',
            user='redes', #Usuario
            password='1234', #Senha
            db='xqdl', #Nome do banco
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)
    except:
        print("Erro conexao com o banco!")
        exit()

    HOST = '10.0.23.131'
    PORT = 13250
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Tracker Servidor
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((HOST, PORT))
    while True:
        serverSocket.listen(5)
        try:
            conn, addr = serverSocket.accept()
            print('Conexao estabelicida!')
            _thread.start_new_thread(clientRecv, (conn, addr, connection)) #Thread
        except:
            print("Erro!")
    conn.close()

main()