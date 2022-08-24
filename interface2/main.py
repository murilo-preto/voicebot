#### IMPORTS ####
import tkinter as tk
from tkinter import ttk
import socket

#### SOCKET CONFIG ####
header_len = 10
ip = "192.168.0.2"
port = 1500
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#### DEF ####


#### GUI ####
LARGE_FONT = ('Times New Roman', 20)  # Fonte para títulos
MAIN_FONT = ('Times New Roman', 14)  # Fonte padrão


class voicebotClass(tk.Tk):  # Root
    def __init__(self, *args, **krwags):
        tk.Tk.__init__(self, *args, **krwags)

        tk.Tk.wm_title(self, 'VoiceBot')
        tk.Tk.wm_geometry(self, '525x525')
        tk.Tk.wm_resizable(self, False, False)

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (loginPage, insertInfoPage, endingPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(loginPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class loginPage(tk.Frame):  # Página inicial
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        def validateLogin():
            if len(passwordEntry.get()) != 0:
                controller.show_frame(insertInfoPage)

        title = ttk.Label(self,
                          text='Bem vindo(a),\ndigite suas credenciais para começar:',
                          font=LARGE_FONT,
                          justify=tk.CENTER)

        title.pack(expand=True, padx=(10, 10), pady=(0, 0))

        ttk.Label(self, text="Usuário:", font=MAIN_FONT).pack()
        userEntry = ttk.Entry(self, width=40)
        userEntry.pack(pady=(0, 10))

        ttk.Label(self, text="Senha:", font=MAIN_FONT).pack()
        passwordEntry = ttk.Entry(self, show='*', width=40)
        passwordEntry.pack(pady=(0, 100))

        sendLogin = ttk.Button(self, text="Validar dados", command=lambda: validateLogin(), width=20)
        sendLogin.pack(padx=(0, 10), pady=(10, 50))


class insertInfoPage(tk.Frame):  # Gráfico em barra
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        def validateInfo():
            if len(weightEntry.get()) != 0:
                controller.show_frame(endingPage)

        title = ttk.Label(self,
                          text='Preencha os campos abaixo:',
                          font=LARGE_FONT,
                          justify=tk.CENTER)

        title.pack(expand=True, padx=(10, 10), pady=(0, 0))

        ttk.Label(self, text="Qual o seu peso, em Kg, medido hoje?\n Digite um número:", font=MAIN_FONT, justify=tk.CENTER).pack()
        weightEntry = ttk.Entry(self, width=10, justify=tk.CENTER)
        weightEntry.pack(pady=(0, 300))

        returnButton = ttk.Button(self, text="Continuar", command=lambda: validateInfo(), width=20)
        returnButton.pack(padx=(10, 10), pady=(10, 10))


class endingPage(tk.Frame):  # Gráfico em barra
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        title = ttk.Label(self,
                          text='Dados salvos com sucesso,\naté breve.',
                          font=LARGE_FONT,
                          justify=tk.CENTER)

        title.pack(expand=True, padx=(10, 10), pady=(0, 0))


app = voicebotClass()
app.mainloop()
