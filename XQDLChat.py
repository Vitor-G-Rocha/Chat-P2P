from tkinter import *
import tkinter as tk
from tkinter import messagebox
import socket
import os
import _thread
import pymysql.cursors #Banco
from XQDLBibliotecas import *
from XQDLfileserver import *
from XQDLfileclient import *
from XQDLVoiceCliente import *
from XQDLVoiceServidor import *

def chatThread(meu_PORT, meu_IP, chat_PORT, alvo_IP, text, msgArea, userNome, tFrame, root): #Thread que trata do chat
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                    #meu_IP = SERVIDOR, alvo_IP = Cliente
    result = s.connect_ex((alvo_IP, chat_PORT)) #Tenta conexão com o alvo, caso não consiga ele assume o servidor, caso contrario, cliente
    if result == 0: #Client
        print("Cliente")
        clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        clientSocket.connect((alvo_IP, chat_PORT))
        Button(tFrame, command = lambda: _thread.start_new_thread(fileTransferServer, (clientSocket, meu_IP)), text="Transferir",font=("Lucida Console", 11, "bold")).pack(side=BOTTOM)
        Button(tFrame, command = lambda: _thread.start_new_thread(mainVoiceServer, (clientSocket, meu_IP)), text="VoIP",font=("Lucida Console", 11, "bold")).pack(side=BOTTOM)
        _thread.start_new_thread(clientRecv, (clientSocket, text, msgArea, userNome, alvo_IP)) #Thread para tratar o Recv do cliente
        msgArea.bind('<Return>', lambda e: clienteChat(msgArea.get(), text, msgArea, clientSocket))
        root.protocol("WM_DELETE_WINDOW", lambda: fecharConexaoC(clientSocket, root))
    else: #Server
        print("Servidor")
        msgArea.bind('<Return>', lambda e: serverChat(msgArea.get(), text, msgArea, conn))
        try: #Recv do Servidor
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocket.bind((meu_IP, chat_PORT))
            Button(tFrame, command = lambda: _thread.start_new_thread(fileTransferServer, (conn, meu_IP)), text="Transferir",font=("Lucida Console", 11, "bold")).pack(side=BOTTOM)
            Button(tFrame, command = lambda: _thread.start_new_thread(mainVoiceServer, (conn, meu_IP)), text="VoIP",font=("Lucida Console", 11, "bold")).pack(side=BOTTOM)
            while True:
                serverSocket.listen(5)
                try:
                    conn, addr = serverSocket.accept()
                    root.protocol("WM_DELETE_WINDOW", lambda: fecharConexaoS(conn, root, serverSocket))
                    try:
                        while True:
                            data = conn.recv(4096).decode() #Server recv / insere msg na area de texto
                            if (data):
                                if(str(data) == 'TRANSFER_FILE_REQUISITION_357159'):
                                    fileTransferClient(alvo_IP)
                                    pass
                                elif(str(data) == 'VOICE_CHAT_REQUEST_357159'):
                                    mainVoiceClient(alvo_IP)
                                    pass
                                else:
                                    text.config(state=NORMAL)
                                    text.insert(INSERT, "["+userNome+"]:"+data+"\n")
                                    text.config(state=DISABLED)
                                    text.see("end")
                            else:
                                break
                                conn.close()
                    except socket.error as msgS:
                        print("ERROR: %s" % msgS)
                except:
                    print("Erro Accept!")
                    serverSocket.close()
                    break
        except:
            print("Socket Servidor Error!")


def clienteChat(msg, text, msgArea, clientSocket): #Funcao que trata 'send' do cliente
    if(msg == ''):
        pass
    else:
        try:
            text.config(state=NORMAL)
            text.insert(INSERT, "[Eu:]"+msg+"\n")
            clientSocket.send(msg.encode())
            text.config(state=DISABLED)
            text.see("end")
            msgArea.delete(0, 'end')
            return None
        except:
            print("ERROR CLIENT")

def serverChat(msg, text, msgArea, conn): #Funcao que trata 'send' do servidor
    if(msg == ''):
        pass
    else:
        try:
            text.config(state=NORMAL)
            text.insert(INSERT, "[Eu:]"+msg+"\n")
            conn.send(msg.encode())
            text.config(state=DISABLED)
            text.see("end")
            msgArea.delete(0, 'end')
            return None
        except:
            print("ERROR SERVER")

def clientRecv(clientSocket, text, msgArea, userNome, alvo_IP): #Thread pra tratar Recv do Cliente e inserir msg recebida na area de texto
    try:
        while True:
            dataC = clientSocket.recv(4096).decode()
            if(dataC):
                if(str(dataC) == 'TRANSFER_FILE_REQUISITION_357159'):
                    fileTransferClient(alvo_IP)
                    pass
                elif(str(dataC) == 'VOICE_CHAT_REQUEST_357159'):
                    mainVoiceClient(alvo_IP)
                    pass
                else:
                    text.config(state=NORMAL)
                    text.insert(INSERT, "["+userNome+"]:"+dataC+"\n")
                    text.config(state=DISABLED)
                    text.see("end")
            else:
                break
                clientSocket.close()
    except:
        print("Recv Client ERROR")
        clientSocket.close()

def fecharConexaoC(clientSocket, root):
    clientSocket.close()
    root.destroy()
#Funcao fechar as conexoes e a janela
def fecharConexaoS(conn, root, serverSocket):
    conn.close()
    serverSocket.close()
    root.destroy()

def mainChat(var, connection, userCheck):
    #Setup
    if(var.get() == "Selecione..." or var.get() == "Nenhum amigo online!"):
        return messagebox.showinfo("Error!" , "Selecione um amigo para conversar!")
    else:
        root = Toplevel()     #Janela Principal
        bgVar = "#333333"
        root.title("Conversando com "+"["+str(var.get())+"]")
        root.resizable(width=False, height=False) #Fazer janela ficar nao redimensionavel
        root.geometry('{}x{}'.format("800", "600")) #Setar tamanho da janela
        root.configure(background = bgVar)
        defaultFont = "Lucida Console" #Fonte padrao usada
        center(root)

        #Top Frame
        tFrame = Frame(root)
        tFrame.config(background=bgVar)
        tFrame.pack(fil=BOTH, expand=YES)
        msgArea = Entry(tFrame, width=118) #Cria area de texto para usuario
        
        #Area de Texto
        msgArea.focus()
        msgArea.pack(side=BOTTOM)
        #Text Area
        text = Text(tFrame, cursor="arrow")
        text.config(state=DISABLED, font=(defaultFont, 11))
        text.pack()
        
        userNome = str(var.get())
        try: #Pegando todas informacoes necessarias para conexao entre os 2 clientes
            with connection.cursor() as cursor:
                sqlQuery = "SELECT `user_IP` FROM `user` WHERE `nome_completo`=%s" #Query
                result = cursor.execute(sqlQuery, userNome) #Executa a Query
                resultSQL = [item['user_IP'] for item in cursor.fetchall()]

                sqlQuery1 = "SELECT `user_PORT` FROM `user` WHERE `nome_completo`=%s" #Query
                result1 = cursor.execute(sqlQuery1, userNome) #Executa a Query
                resultSQL1 = [item['user_PORT'] for item in cursor.fetchall()]

                sqlQuery2 = "SELECT `user_PORT` FROM `user` WHERE `user_nome`=%s" #Query
                result2 = cursor.execute(sqlQuery2, userCheck[0]) #Executa a Query
                resultSQL2 = [item['user_PORT'] for item in cursor.fetchall()]

                sqlQuery3 = "SELECT `user_IP` FROM `user` WHERE `user_nome`=%s" #Query
                result3 = cursor.execute(sqlQuery3, userCheck[0]) #Executa a Query
                resultSQL3 = [item['user_IP'] for item in cursor.fetchall()]

                #chat_PORT = int(resultSQL1[0])
                chat_PORT = 42455
                alvo_IP = str(resultSQL[0])

                meu_PORT = int(resultSQL2[0]) 
                meu_IP = str(resultSQL3[0])
        except:
            messagebox.showinfo("Error!" , "SQL ERROR!")
        try:
            _thread.start_new_thread(chatThread, (meu_PORT, meu_IP, chat_PORT, alvo_IP, text, msgArea, userNome, tFrame, root)) #Thread
        except:
            print("Thread Error")
        root.mainloop()