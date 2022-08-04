import tkinter as tk
from tkinter import ttk
import socket
import threading

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
    except ConnectionRefusedError:
        update_label_txt(mainLabel, "Não foi possível conectar ao servidor,\ntente novamente mais tarde.")


def send_txt_helper(txt):
    msg = f"{len(txt):<{HEADER_LEN}}" + txt
    client_socket.send(msg.encode())


def send_txt(texto):
    infoArquivo = f"texto{SEPARADOR}{len(texto)}"
    send_txt_helper(infoArquivo)
    send_txt_helper(texto)


def closing_protocol():
    root.destroy()


def receive_txt():
    None


def receive_audio():
    None


def update_label_txt(label, text):
    label["text"] = text


# Variáveis
texto_principal = "Bem vindo(a),\naperte o botão abaixo para iniciar:"
start_protocol_threading = lambda: threading.Thread(target=start_protocol).start()

# Config. Soquete
client_socket = socket.socket()

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
