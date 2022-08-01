"""
    1. Ouvir audio do microfone
    2. Reconhecer texto via google recog.

    3. Enviar texto ao servidor
    4. Receber resposta do servidor

    5. Rodar audio recebido do servidor

    Bônus - campo de digitação, exibir resposta do servidor
"""


import socket
import os

# Iniciar constantes
SERVER_IP = "192.168.0.11"
SERVER_PORT = 5001
SEPARADOR = "<SEPARATOR>"  # Separador de texto auxiliar
TAMANHO_BUFFER = 4096  # Qtd de bytes a serem enviados por scan
NOME_ARQUIVO = "audio.mp3"  # Nome do arquivo a ser enviado
HEADER_LEN = 10  # Tamanho header da msg


# Funcoes
def enviartxt(txt):
    msg = f"{len(txt):<{HEADER_LEN}}" + txt
    client_socket.send(msg.encode())


def enviarAudioIndexado(caminhoAudio):
    infoArquivo = f"audio{SEPARADOR}{os.path.getsize(caminhoAudio)}"
    enviartxt(infoArquivo)

    with open(caminhoAudio, "rb") as f:
        while True:
            bytesLidos = f.read(TAMANHO_BUFFER)  # Ler Bytes
            if not bytesLidos:  # Envio encerrado
                break
            client_socket.sendall(bytesLidos)  # Enviar Bytes lidos


def enviarTextoIndexado(texto):
    infoArquivo = f"texto{SEPARADOR}{len(texto)}"
    enviartxt(infoArquivo)
    enviartxt(texto)


client_socket = socket.socket()
print(f"[*] Conectando a {SERVER_IP}:{SERVER_PORT}")
client_socket.connect((SERVER_IP, SERVER_PORT))  # Conectar ao servidor
print("[*] Conectado")

while True:
    tipoArquivo = "audio"

    if tipoArquivo == "audio":
        enviarAudioIndexado(NOME_ARQUIVO)

    if tipoArquivo == "texto":
        texto = input("txt: ")
        enviarTextoIndexado(texto)
