import socket
import pyaudio
import wave
import time
from tkinter import *
from tkinter.filedialog import askopenfilename

def encerrarVoice(root, conn, stream, p):
    stream.stop_stream()
    stream.close()
    p.terminate()
    conn.close()
    root.destroy()

def mainVoiceServer(socketV, HOST):
    root = Toplevel()
    root.title("Voice Chat")
    Label(root, text = "Voice Chat").pack()
    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 20000
    RECORD_SECONDS = 4000

    voiceRequestMsg = 'VOICE_CHAT_REQUEST_357159'
    socketV.send(voiceRequestMsg.encode())

    PORT = 17777
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    respostaV = conn.recv(1024).decode()
    if(str(respostaV) == 'yes'):
        p = pyaudio.PyAudio()

        # receber dados
        stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)

        # enviar dados
        stream2 = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

        root.protocol("WM_DELETE_WINDOW", lambda: encerrarVoice(root, conn, stream, p))
        data='a'
        while data != '':
            try:        #recebendo dados
                data = conn.recv(1024)
                stream.write(data)
            except:
                break

            try:        # enviando dados
                data2  = stream2.read(CHUNK)
                conn.sendall(data2)
            except:
                break
        encerrarVoice(root, conn, stream, p)
        return None
    else:
        root.destroy()
        conn.close()
        return None
    root.mainloop()