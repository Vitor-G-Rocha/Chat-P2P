import os
import socket
import time
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

def fileTransferServer(socketT, transferIp): #transferIp = Ip de quem faz requisição de file transfer
    transferMsg = 'TRANSFER_FILE_REQUISITION_357159'
    portTransfer = 42460
    socketST = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketST.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(transferIp)
    socketST.bind((transferIp, portTransfer))
    socketT.send(transferMsg.encode())
    while True:
        socketST.listen(5)
        try:
            conn, addr = socketST.accept()
        except:
            print("Accept Error! File Server")
        respostaT = conn.recv(1024).decode()
        if(str(respostaT) == 'yes'):
            filepath = askopenfilename()
            maxSize = os.path.getsize(str(filepath))
            splitFile = filepath.split('/')
            tamanho = len(splitFile) - 1
            fileName = splitFile[tamanho]
            conn.send(fileName.encode())
            fileToSend = open(str(filepath), 'rb')
            while True:
                data = fileToSend.readline()
                if data:
                    conn.send(data)
                else:
                    break
            fileToSend.close()
            conn.close()
            return None
        else:
            conn.close()
            return None