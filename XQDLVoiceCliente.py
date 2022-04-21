import socket
import pyaudio
import wave
from tkinter import *
from tkinter import messagebox
import time

def encerrarVoice(root, s, stream, p):
    stream.stop_stream()
    stream.close()
    p.terminate()
    s.close()
    root.destroy()

def mainVoiceClient(HOST):
    root = Toplevel()
    root.title("Voice Chat")
    Label(root, text = "Voice Chat").pack()
    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 20000

    PORT = 17777
    time.sleep(.500)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    resultVoice = messagebox.askquestion("Confirmação", "Deseja iniciar o Voice Chat?", icon='warning')
    if (resultVoice == 'yes'):
        s.send(resultVoice.encode())
        time.sleep(.250)
        p = pyaudio.PyAudio() #Instanciando Pyaudio, inicializando
        # enviar dados
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)


        # receber dados
        stream2 = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK)
        root.protocol("WM_DELETE_WINDOW", lambda: encerrarVoice(root, s, stream, p))
        data2='a'
        while data2 != '':
            try:       # envio
                data  = stream.read(CHUNK)
                s.sendall(data) 
            except:
                break

            try:       # recebendo
                data2 = s.recv(1024)
                stream2.write(data2)
            except:
                break
        encerrarVoice(root, s, stream, p)
        return None
    else:
        s.close()
        root.destroy()
        return None
    root.mainloop()