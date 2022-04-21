import os
import socket
from tkinter import *
from tkinter import messagebox
import time
#CRIAR ROOT WITHDRAW
def fileTransferClient(transferIp):
    portTransfer = 42460
    time.sleep(.500)
    ctSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctSocket.connect((transferIp, portTransfer))
    resultFile = messagebox.askquestion("Confirmação", "Deseja aceitar o arquivo?", icon='warning')
    if (resultFile == 'yes'):
        ctSocket.send(resultFile.encode())
        filename = ctSocket.recv(1024).decode()
        fname = open(str(filename), 'wb')
        while True:
            strng = ctSocket.recv(1024)
            if(strng):
                fname.write(strng)
            else:
                fname.close()
                break
        ctSocket.close()
        return None
    else:
        ctSocket.send(resultFile.encode())
        ctSocket.close()
        return None