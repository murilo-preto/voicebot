#### IMPORTS ####
import tkinter as tk
from tkinter import ttk
import socket
import threading
import speech_recognition as sr
from playsound import playsound
import os
import textwrap


# Constantes
SERVER_IP = "localhost"
SERVER_PORT = 5002
SEPARADOR = "<SEPARATOR>"  # Separador de texto auxiliar
TAMANHO_BUFFER = 4096  # Qtd de bytes a serem enviados por scan
NOME_ARQUIVO = "audio.mp3"  # Nome do arquivo a ser enviado
HEADER_LEN = 10  # Tamanho header da msg


# Def
def send_txt(txt):
    if isinstance(txt, str):
        msg = f"{len(txt):<{HEADER_LEN}}" + txt
        client_socket.send(msg.encode())


def send_txt_indexado(texto):
    if isinstance(texto, str):
        infoArquivo = f"texto{SEPARADOR}{len(texto)}"
        send_txt(infoArquivo)
        send_txt(texto)


def receive_txt(client_socket):
    try:
        tamanhotxt = client_socket.recv(HEADER_LEN).decode()
        tamanhotxt = int(tamanhotxt.strip())
        txt = client_socket.recv(tamanhotxt).decode()
        return txt
    except:
        return False


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


# Carregar funções:
r = sr.Recognizer()
client_socket = socket.socket()


#### GUI ####
LARGE_FONT = ('Times New Roman', 20)  # Fonte para títulos
MAIN_FONT = ('Times New Roman', 14)  # Fonte padrão


class voicebotClass(tk.Tk):  # Root
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, 'VoiceBot')
        tk.Tk.wm_geometry(self, '700x400')
        tk.Tk.wm_resizable(self, False, False)

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (socketPage, loginPage, insertInfoPage, endingPage, anamnesePage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(socketPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class socketPage(tk.Frame):  # Página inicial
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        def connect2server():
            socketTitle["text"] = "Tentando conectar ao servidor,\naguarde um momento."
            try:
                #client_socket.connect((SERVER_IP, SERVER_PORT))  # Conectar ao servidor
                socketTitle["text"] = "Conexão bem sucedida,\niniciando consulta."
                controller.show_frame(loginPage)
            except ConnectionRefusedError:
                socketTitle["text"] = "Não foi possível conectar ao servidor,\ntente novamente mais tarde."

        socketTitle = ttk.Label(self,
                          text='Bem vindo(a),\naperte o botão abaixo para começar:',
                          font=LARGE_FONT,
                          justify=tk.CENTER)

        socketTitle.pack(expand=True, padx=(10, 10), pady=(0, 0))

        sendLogin = ttk.Button(self, text="Conectar ao servidor", command=lambda: connect2server(), width=20)
        sendLogin.pack(padx=(0, 10), pady=(10, 50))


class loginPage(tk.Frame):  # Página inicial
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        def validateLogin():
            if len(passwordEntry.get()) != 0:
                controller.show_frame(insertInfoPage)

        title = ttk.Label(self,
                          text='Digite suas credenciais\nnos campos indicados abaixo:',
                          font=LARGE_FONT,
                          justify=tk.CENTER)

        title.pack(expand=True, padx=(10, 10), pady=(0, 0))

        ttk.Label(self, text="Usuário:", font=MAIN_FONT).pack()
        userEntry = ttk.Entry(self, width=40)
        userEntry.pack(pady=(0, 20))

        ttk.Label(self, text="Senha:", font=MAIN_FONT).pack()
        passwordEntry = ttk.Entry(self, show='*', width=40)
        passwordEntry.pack(pady=(0, 100))

        sendLogin = ttk.Button(self, text="Validar dados", command=lambda: validateLogin(), width=20)
        sendLogin.pack(padx=(0, 10), pady=(10, 30))


class insertInfoPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        def validateInfo():
            if len(weightEntry.get()) != 0:
                if weightEntry.get() == "1":
                    controller.show_frame(anamnesePage)
                else:
                    controller.show_frame(endingPage)

        title = ttk.Label(self,
                          text='Preencha os campos abaixo:',
                          font=LARGE_FONT,
                          justify=tk.CENTER)

        title.pack(expand=True, padx=(10, 10), pady=(0, 0))

        ttk.Label(self, text="Qual o seu peso, em Kg, medido hoje?\nDigite um número:", font=MAIN_FONT, justify=tk.CENTER).pack()
        weightEntry = ttk.Entry(self, width=10, justify=tk.CENTER)
        weightEntry.pack(padx=(10, 10), pady=(0, 160))

        returnButton = ttk.Button(self, text="Continuar", command=lambda: validateInfo(), width=20)
        returnButton.pack(padx=(10, 10), pady=(10, 30))


class anamnesePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        def anamnese():
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
                            anamneseTitle["text"] = texto

                        elif tipoArquivo == "audio":
                            with open(NOME_ARQUIVO, "wb") as f:  # Baixar audio encapsulado
                                bytesLidos = client_socket.recv(tamanhoArquivo)
                                f.write(bytesLidos)

                            playsound(NOME_ARQUIVO)
                            print("Audio reproduzido")
                            os.remove(NOME_ARQUIVO)

                            while resposta_usuario != False:
                                resposta_usuario = voice2txt()  # Ouvir usuario

                            # resposta_usuario = "sim"

                            send_txt_indexado(resposta_usuario)

        anamneseTitle = ttk.Label(self,
                          text='Alerta ganho de peso -> Anamnese',
                          font=LARGE_FONT,
                          justify=tk.CENTER)

        anamneseTitle.pack(expand=True, padx=(10, 10), pady=(0, 0))


class endingPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        title = ttk.Label(self,
                          text='Dados salvos com sucesso,\naté breve.',
                          font=LARGE_FONT,
                          justify=tk.CENTER)

        title.pack(expand=True, padx=(10, 10), pady=(0, 0))


app = voicebotClass()
app.mainloop()
