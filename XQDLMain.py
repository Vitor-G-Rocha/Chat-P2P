from tkinter import *
from tkinter import messagebox
import socket
import pymysql.cursors
from XQDLBibliotecas import *
from XQDLChat import *

#Globais
bgVar = "#333333"
defaultFont = "Lucida Console" #Fonte padrao usada
list_amigos = []

#Funcao que mostra os amigos, tanto offline quanto online
def refreshFriend(resultSQL, connection, leftFrame, userCheck, flag, buttonReference, optionReference, var): 
    if(flag == 0):
        with connection.cursor() as cursor:
            i = 0
            lista_Button = []
            cor = ""
            sqlQuery2 = "select count(*) from user P join buddy B on P.user_ID = B.person_id1 and B.person_id1 = P.user_ID where user_nome = %s"
            result2 = cursor.execute(sqlQuery2, userCheck[0])
            resultSQL2 = [item['count(*)'] for item in cursor.fetchall()]
            if (resultSQL2[0] == 0):
                messagebox.showinfo("SQL" , "Você nao tem amigos! :(")
                list_amigos.append("Nenhum amigo online!")
                labelUser = Label(leftFrame, text = "Nenhum amigo online!", background = "grey")
                labelUser.pack(fil=BOTH)
                lista_Button.append(labelUser)
                return (lista_Button, 0, 0)
            else:
                while(i < resultSQL2[0]):
                    sqlQuery = "SELECT `status` FROM `user` WHERE `nome_completo`=%s" #Query
                    result = cursor.execute(sqlQuery, resultSQL[i]) #Executa a Query
                    resultSQL1 = [item['status'] for item in cursor.fetchall()]
                    connection.commit()
                    if(resultSQL1[0] == 1): #Se 'Status' do amigo for 1 == online
                        list_amigos.append(resultSQL[i])
                        buttonUser = Label(leftFrame, text = resultSQL[i], background = "green")
                    else: #Senao offline
                        buttonUser = Label(leftFrame, text = resultSQL[i], background = "grey")
                    buttonUser.pack(fil=BOTH)
                    lista_Button.append(buttonUser) #Lista usada para guardar referencia dos botoes, e do 'Option Menu'
                    i = i +1
                var = StringVar(leftFrame)
                if not(list_amigos): #Se lista vazia, nao tem amigos online!
                    option = OptionMenu(leftFrame, var, "Nenhum amigo online!")
                    var.set("Selecione...")
                    option.pack()
                    button = Button(leftFrame, text="Conversar", command = lambda: mainChat(var, connection, userCheck))
                    button.pack()
                else: #Senao preenche o 'OptionMenu' com os amigos online
                    option = OptionMenu(leftFrame, var, *list_amigos)
                    var.set("Selecione...") # initial value
                    option.pack()
                    button = Button(leftFrame, text="Conversar", command = lambda: mainChat(var, connection, userCheck))
                    button.pack()
                return (lista_Button, option, var)
    else: #Botao 'Atualizar'
        list_amigos[:] = [] #Esvazia a lista
        m = optionReference.children ['menu']
        var.set("Selecione...") 
        with connection.cursor() as cursor:
            i = 0
            cor = ""
            sqlQuery2 = "select count(*) from user P join buddy B on P.user_ID = B.person_id1 and B.person_id1 = P.user_ID where user_nome = %s"
            result2 = cursor.execute(sqlQuery2, userCheck[0])
            resultSQL2 = [item['count(*)'] for item in cursor.fetchall()]
            while(i < resultSQL2[0]):
                sqlQuery = "SELECT `status` FROM `user` WHERE `nome_completo`=%s" #Query
                result = cursor.execute(sqlQuery, resultSQL[i]) #Executa a Query
                resultSQL1 = [item['status'] for item in cursor.fetchall()]
                buttonUser = buttonReference[i]
                if(resultSQL1[0] == 1):
                    list_amigos.append(resultSQL[i])
                    buttonUser.config(text = resultSQL[i], background = "green")
                else:
                    buttonUser.config(text = resultSQL[i], background = "grey")
                buttonUser.pack(fil=BOTH)
                connection.commit()
                i = i +1
            m.delete(0,END) # Apaga todos os valores do meu Option Menu
            for val in list_amigos: #preenche o option menu com os valores atualizados
                m.add_command(label=val,command=lambda v=var,l=val:v.set(l))

def setupMain(resultSQL, connection, userCheck, clientSocket):
    #Setup
    flag = 0 #Flag 0 == aberto pela primeira vez, 1 para o botao de atualizar
    root = Tk()     #Janela Principal
    root.resizable(width=False, height=False) #Fazer janela ficar nao redimensionavel
    root.geometry('{}x{}'.format("800", "450")) #Setar tamanho da janela
    root.title("XQDL-Messenger")
    center(root)
    root.configure(background = bgVar)
    #Left Frame
    leftFrame = Frame(root)
    leftFrame.grid(row = 0, column = 0)
    label_title = Label(leftFrame, text = "Amigos", fg = "black", width = 12)
    label_title.config(font=(defaultFont, 16, "bold"))
    label_title.pack()
    addVar = StringVar()
    usuario = Label(leftFrame, text="Nome Amigo:", foreground="#000") #Cria label para usuario
    usuario.pack()
    usuario.config(font=(defaultFont, 11))
    DEBUG = Label(leftFrame, text = "DEBUG", fg = "black")
    DEBUG.config(font=(defaultFont, 12, "bold"))
    DEBUG.pack()
    root.protocol("WM_DELETE_WINDOW", lambda: fechar(root, userCheck, connection, clientSocket)) #Altera status do Usuario para Offline quando ele sai do programa
    buttonReference, optionReference, varReference = refreshFriend(resultSQL, connection, leftFrame, userCheck, flag, 0, 0, 0)
    flag = 1
    buttonRefresh = Button(leftFrame, command = lambda: refreshFriend(resultSQL, connection, leftFrame, userCheck, flag, buttonReference, optionReference, varReference))
    buttonRefresh.pack()
    buttonRefresh.config(text="Atualizar", activebackground="green")
    root.mainloop()

def mainLogin(userCheck, connection, clientSocket): #UserCheck = Usuario #MAIN
    with connection.cursor() as cursor: #Banco de dados
        sqlQuery1 = "SELECT `user_ID` FROM `user` WHERE `user_nome` = %s"
        result1 = cursor.execute(sqlQuery1, userCheck)
        resultSQL1 = [item['user_ID'] for item in cursor.fetchall()]
        sqlQuery = "SELECT `nome_completo` FROM `user` u INNER JOIN `buddy` b ON b.person_id2 = u.`user_ID` WHERE b.person_id1 = %s" #Query
        result = cursor.execute(sqlQuery, resultSQL1) #Executa a Query
        resultSQL = [item['nome_completo'] for item in cursor.fetchall()] #Pega o resultado do Query e remove o pedaco 'user_amigos' da tupla
        if result1 == 0: #Verifica se o resultado do sqlQuery foi bem sucedido se 0, usuario ou senha nao foram encontrados no DB
            messagebox.showinfo("Erro!", "SQL ERRADO")
        else:
            setupMain(resultSQL, connection, userCheck, clientSocket)

def fechar(root, userCheck, connection, clientSocket): #Funcao que encerra conexao e sai do programa
    clientSocket.close()
    root.destroy()
    with connection.cursor() as cursor:
        sqlQuery = "UPDATE `user` SET `status`=%s, `user_IP`=%s, `user_PORT`=%s WHERE `user_nome`=%s"
        cursor.execute(sqlQuery, (0, '0.0.0.0', '0', userCheck))
        connection.commit()
        connection.close()

'''def addAmigo(connection, addVar, userSQL, entry):
    queryGet = addVar.get()
    with connection.cursor() as cursor:
        sqlQuery1 = "SELECT `user_ID` FROM `user` WHERE `user_nome`=%s"
        result = cursor.execute(sqlQuery1, (queryGet))
        resultSQL = [item['user_ID'] for item in cursor.fetchall()]
        if result == 0:
            messagebox.showinfo("Erro!", "Nome nao encontrado no banco!")
        else:
            sqlQuery = "INSERT INTO `relacionamento` (`user_id1`, `user_id2`, `status`) VALUES (%s,%s,1)" #Query
            cursor.execute(sqlQuery, (userSQL,resultSQL))
            connection.commit()
            entry.delete(0, END) #Apagando texto da area de texto 'entry' é uma referencia para o campo loginTextUser'''