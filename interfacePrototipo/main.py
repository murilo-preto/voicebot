import tkinter as tk
from tkinter import ttk
import socket
import threading
import speech_recognition as sr
from playsound import playsound
import os
import textwrap



# Iniciar constantes
SERVER_IP = "localhost"
SERVER_PORT = 5001
SEPARADOR = "<SEPARATOR>"  # Separador de texto auxiliar
TAMANHO_BUFFER = 4096  # Qtd de bytes a serem enviados por scan
NOME_ARQUIVO = "audio.mp3"  # Nome do arquivo a ser enviado
HEADER_LEN = 10  # Tamanho header da msg


# Funções
def start_protocol():
    update_label_txt(mainLabel, "Tentando conectar ao servidor,\naguarde um momento.")
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))  # Conectar ao servidor
        update_label_txt(mainLabel, "Conexão bem sucedida,\niniciando consulta.")
        begin_loop = True
    except ConnectionRefusedError:
        update_label_txt(mainLabel, "Não foi possível conectar ao servidor,\ntente novamente mais tarde.")
        begin_loop = False

    if begin_loop:
        update_label_txt(mainLabel, "Iniciando main loop")
        resposta_usuario = "Murilo"
        send_txt_indexado(resposta_usuario)  # Enviar o que foi ouvido ao servidor
        while True:
            if resposta_usuario != False:
                infoArquivo = receive_txt(client_socket)  # Receber resposta do servidor
                if infoArquivo != False:
                    tipoArquivo, tamanhoArquivo = infoArquivo.split(SEPARADOR)
                    tamanhoArquivo = int(tamanhoArquivo)

                    if tipoArquivo == "texto":
                        texto = receive_txt(client_socket)  # Receber texto
                        texto = wrap_txt(texto)
                        update_label_txt(mainLabel, texto)

                    elif tipoArquivo == "audio":
                        with open(NOME_ARQUIVO, "wb") as f:  # Baixar audio encapsulado
                            bytesLidos = client_socket.recv(tamanhoArquivo)
                            f.write(bytesLidos)

                        playsound(NOME_ARQUIVO)
                        print("Audio reproduzido")
                        os.remove(NOME_ARQUIVO)

                        #resposta_usuario = voice2txt()  # Ouvir usuario
                        resposta_usuario = "sim"
                        send_txt_indexado(resposta_usuario)


def send_txt(txt):
    msg = f"{len(txt):<{HEADER_LEN}}" + txt
    client_socket.send(msg.encode())


def send_txt_indexado(texto):
    infoArquivo = f"texto{SEPARADOR}{len(texto)}"
    send_txt(infoArquivo)
    send_txt(texto)


def closing_protocol():
    root.destroy()


def receive_txt(client_socket):
    try:
        tamanhotxt = client_socket.recv(HEADER_LEN).decode()
        tamanhotxt = int(tamanhotxt.strip())
        txt = client_socket.recv(tamanhotxt).decode()
        return txt
    except:
        return False


def receive_audio():
    with open(NOME_ARQUIVO, "wb") as f:  # Baixar audio encapsulado
        while True:
            bytesLidos = client_socket.recv(TAMANHO_BUFFER)
            if not bytesLidos:
                break
            f.write(bytesLidos)


def update_label_txt(label, txt):
    label["text"] = txt


def voice2txt():
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Ouvindo")
            audio = r.listen(source)
            said = r.recognize_google(audio, language="pt-BR")
            print("Foi dito: " + said)
            return said
    except:
        return False


def wrap_txt(txt):
    aux_str = ""
    print(txt)
    newstr = textwrap.wrap(text=txt, width=40)
    print(newstr)
    for i in newstr:
        aux_str += i + ' \n'
    return aux_str


# Variáveis
texto_principal = "Bem vindo(a),\naperte o botão abaixo para iniciar:"
start_protocol_threading = lambda: threading.Thread(target=start_protocol).start()

# Config. Soquete
client_socket = socket.socket()

# Startup de funções
r = sr.Recognizer()

# Interface:
root = tk.Tk()
root.geometry("640x360")
root.resizable(False, False)
root.title('VoiceBot')

# Frame
frame_voicebot = ttk.Frame(root)
frame_voicebot.pack(padx=10, fill='x', expand=True)

# Texto principal
mainLabel = tk.Label(frame_voicebot, text=texto_principal, font="Times 20")
mainLabel.pack(fill='x', expand=True, pady=(0, 30))

# Botão — Iniciar reconhecimento de voz
b_registrar_user = ttk.Button(frame_voicebot, text="Iniciar consulta", command=start_protocol_threading, width=25)
b_registrar_user.pack(fill="none", expand=True, pady=(0, 30))


root.protocol("WM_DELETE_WINDOW", closing_protocol)

root.mainloop()
