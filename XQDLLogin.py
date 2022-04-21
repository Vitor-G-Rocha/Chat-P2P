from tkinter import *
from tkinter import messagebox
import socket
import pymysql.cursors
from XQDLMain import *
from XQDLBibliotecas import *

#Setup
root = Tk()     #Janela Principal
root.resizable(width=False, height=False) #Fazer janela ficar nao redimensionavel
center(root) #Centralizar
root.geometry('{}x{}'.format("350", "190")) #Setar tamanho da janela
bgVar = "#333333"
root.configure(background = bgVar)
#destroy Frame
destroyFrame = Frame(root)
destroyFrame.grid(row = 0, column = 1)
#Top Frame
topFrame = Frame(root)
topFrame.grid(row = 1, column = 0)
topFrame.configure(background = bgVar)
#Bottom Frame
bottomFrame = Frame(root)
bottomFrame.grid(row = 2, column = 0)
bottomFrame.configure(background = bgVar)

defaultFont = "Lucida Console" #Fonte padrao usada

def loginServer():
    userCheck = userVar.get()
    passCheck = passVar.get()
    if userCheck == '':
        messagebox.showinfo("Error!" , "Campo de usuário vazio!")
        loginTextUser.focus()
    elif passCheck == '':
        messagebox.showinfo("Error!" , "Campo de senha vazio!")
        loginTextPass.focus()
    else:
        HOST = '10.0.23.131'    # Ip do Host alvo(tracker)
        PORT = 13250         # Porta do Tracker
        #Conexao usando Socket(TCP)
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        resultado = clientSocket.connect_ex((HOST, PORT))
        if resultado == 0: #Tenta conexao com o tracker pra verificar se ele está on ou offline
            try: #Conexao com o banco de dados
                connection = pymysql.connect(host='10.0.23.131',
                             user='redes', #Usuario
                             password='1234', #Senha
                             db='xqdl', #Nome do banco
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
                #Aqui pode executar comandos SQL
                with connection.cursor() as cursor:
                    sqlQuery = "SELECT `user_nome`, `user_senha` FROM `user` WHERE `user_nome`=%s AND `user_senha` =%s" #Query
                    result = cursor.execute(sqlQuery, (userCheck, passCheck)) #Executa a Query
                    resultSQL = [item['user_nome'] for item in cursor.fetchall()] #Guarda o resultado da Query
                    if result == 0: #Verifica se o resultado do sqlQuery foi bem sucedido se 0, usuario ou senha nao foram encontrados no DB
                        messagebox.showinfo("Erro!", "Usuário ou senha nao encontrados!")
                    else: #Passa como parametro, usuario e senha, para outro arquivo e destroi a janela 'Login'
                        root.destroy()
                        clientSocket.send(userCheck.encode()) #Envia para o tracker usuário
                        mainLogin(resultSQL, connection, clientSocket)
            except pymysql.Error:
                messagebox.showinfo("Erro!", "Erro na conexao com o DB!")
        else:
            messagebox.showinfo("Error!" , "Tracker offline!")

'''TITULO'''
root.title("Fly By Night - Messenger")
title = Label(topFrame, text="Fly By Night - Chat/VoiceChat\n", foreground="#ffffff")
title.pack()
title.config(font=(defaultFont, 16, "bold"), background = bgVar)
'''FIM TITULO'''

'''Usuario'''
userVar = StringVar()
usuario = Label(topFrame, text="Usuário:", foreground="#ffffff") #Cria label para usuario
usuario.pack()
usuario.config(font=(defaultFont, 11), background = bgVar)
loginTextUser = Entry(topFrame, textvariable=userVar) #Cria area de texto para usuario
loginTextUser.focus()
loginTextUser.pack()
loginTextUser.bind('<Return>', lambda e: loginServer()) #Botao 'Enter' funcionar
'''FIM USUARIO'''

'''SENHA'''
passVar = StringVar()
senha = Label(topFrame, text="Senha:", foreground="#ffffff") #Cria label para senha
senha.pack()
senha.config(font=(defaultFont, 11), background = bgVar)
loginTextPass = Entry(topFrame, show="*", textvariable=passVar) #Cria area de texto para senha
loginTextPass.pack()
loginTextPass.bind('<Return>', lambda e: loginServer())
'''FIM SENHA'''

'''BOTAO LOGIN'''
buttonLogin = Button(bottomFrame, command = loginServer) #Botao de login
buttonLogin.pack() #Faz botao aparecer
buttonLogin.config(font=(defaultFont, 11, "bold"),text="Login", bg='#242424', foreground="white")
'''FIM BOTaO LOGIN'''

root.mainloop()