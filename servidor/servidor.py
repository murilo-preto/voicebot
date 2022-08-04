import socket
import select
from gtts import gTTS
import os
import aiml

# Iniciar constantes
SERVER_HOST = "localhost"
SERVER_PORT = 5001
SEPARADOR = "<SEPARATOR>"  # Separador de texto auxiliar
TAMANHO_BUFFER = 4096  # Qtd de bytes a serem recebidos por scan
NOME_ARQUIVO = "audio.mp3"  # Nome do arquivo de audio
HEADER_LEN = 10  # Tamanho header da msg


# Funcoes
def receive_txt(client_socket):  # Receber texto, cliente que o envia como argumento
    try:
        tamanhotxt = client_socket.recv(HEADER_LEN).decode()
        tamanhotxt = int(tamanhotxt.strip())
        txt = client_socket.recv(tamanhotxt).decode()
        return txt
    except:
        return False


def send_txt(client_socket, txt):
    msg = f"{len(txt)+10:<{HEADER_LEN}}" + txt
    client_socket.send(msg.encode())


def send_txt_indexed(client_socket, texto):
    infoArquivo = f"texto{SEPARADOR}{len(texto)+10}"
    send_txt(client_socket, infoArquivo)
    send_txt(client_socket, texto)


def send_audio_response(client_socket, response):
    tts = gTTS(text=response, lang='pt-br')
    filename = f'tempname.mp3'
    tts.save(filename)
    send_audio_indexed(client_socket, filename)
    os.remove(filename)


def send_audio_indexed(client_socket, caminhoAudio):
    infoArquivo = f"audio{SEPARADOR}{os.path.getsize(caminhoAudio)}"
    send_txt(client_socket, infoArquivo)

    with open(caminhoAudio, "rb") as f:
        bytesLidos = f.read(os.path.getsize(caminhoAudio))  # Ler Bytes
        client_socket.send(bytesLidos)  # Enviar Bytes lidos


def process_txt(texto):
    if texto is False:  # recebertxt retornou falso: cliente fechou conexao
        lista_soquetes.remove(notified_socket)
        return False
    else:  # indice recebido valido
        tipoArquivo, tamanhoArquivo = texto.split(SEPARADOR)

        if tipoArquivo == "texto":
            texto = receive_txt(notified_socket)  # Receber texto
            return texto


# Init
ai = aiml.Kernel()  # inicialização
ai.learn('voicebot2.xml')  # lê o arquivo principal da AIML e faz referências aos outros

server_socket = socket.socket()
server_socket.bind((SERVER_HOST, SERVER_PORT))

lista_soquetes = [server_socket]  # Lista de todos soquetes conectados

server_socket.listen(5)  # Quantidade de clientes que entram em espera
print(f"[*] Esperando conexoes em {SERVER_HOST}:{SERVER_PORT}")

while True:
    r_list, w_list, x_list = select.select(lista_soquetes, [], lista_soquetes)

    for notified_socket in r_list:
        if notified_socket == server_socket:  # Nova conexao pendente
            notified_socket, endereco = server_socket.accept()
            print(f"[+] {endereco} foi conectado")
            lista_soquetes.append(notified_socket)
        else:  # Nao ha conexoes novas pendentes
            print("[+] Recebendo dados:", notified_socket)
            infoArquivo = receive_txt(notified_socket)
            texto = process_txt(infoArquivo)
            if texto != False:
                name = texto
                said = "ROBOTSTART " + name
                response = ai.respond(said)

                send_txt_indexed(notified_socket, response)
                send_audio_response(client_socket=notified_socket, response=response)

                while texto != "Até logo":
                    infoArquivo = receive_txt(notified_socket)
                    texto = process_txt(infoArquivo)
                    if texto != False:
                        try:
                            response = ai.respond(texto)
                        except:
                            response = "Desculpe, mas não consegui captar o que você disse..."

                        send_txt_indexed(notified_socket, response)
                        send_audio_response(notified_socket, response)

    for notified_socket in x_list:
        lista_soquetes.remove(notified_socket)
