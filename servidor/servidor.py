import socket
import select
import aiml
import bcrypt
import pandas as pd
import os.path


# Iniciar constantes
hostname = socket.gethostname()
ipAddress = socket.gethostbyname(hostname)
SERVER_PORT = 5005
SEPARADOR = "<SEPARATOR>"  # Separador de texto auxiliar
TAMANHO_BUFFER = 4096  # Qtd de bytes a serem recebidos por scan
NOME_ARQUIVO = "audio.mp3"  # Nome do arquivo de audio
NOME_LOG = "log.txt"
HEADER_LEN = 10  # Tamanho header da msg


# Funcoes
def writelog (logpath=NOME_LOG, text=""):
    with open(logpath, 'a') as f:
        f.write(text)
        f.write('\n')

    print(text)


def receive_txt(client_socket):  # Receber texto, cliente que o envia como argumento
    try:
        tamanhotxt = client_socket.recv(HEADER_LEN).decode('utf-8')
        tamanhotxt = int(tamanhotxt.strip())
        txt = client_socket.recv(tamanhotxt).decode('utf-8')
        return txt
    except:
        return False


def send_txt(client_socket, txt):
    txtEncoded = txt.encode('utf-8')
    msg = f"{len(txtEncoded):<{HEADER_LEN}}" + txt
    client_socket.send(msg.encode('utf-8'))


def send_txt_indexed(client_socket, texto, serverIP):
    txtEncoded = texto.encode('utf-8')
    infoArquivo = f"texto{SEPARADOR}{len(txtEncoded)}"
    send_txt(client_socket, infoArquivo)
    send_txt(client_socket, texto)

    writelog(text=f"Servidor ({serverIP}): {texto}")


def process_txt(texto, clienteIP):
    if texto is False:  # recebertxt retornou falso: cliente fechou conexao
        return False
    else:  # indice recebido valido
        tipoArquivo, tamanhoArquivo = texto.split(SEPARADOR)

        if tipoArquivo == "texto":
            texto = receive_txt(notified_socket)  # Receber texto
            writelog(text=f"Cliente ({clienteIP}): {texto}")
            return texto


# Init
ai = aiml.Kernel()  # inicialização
ai.learn('voicebot2.xml')  # lê o arquivo principal da AIML e faz referências aos outros

with open("log.txt", 'w') as f:  # limpa o log de texto
    f.write("")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ipAddress, SERVER_PORT))

lista_soquetes = [server_socket]  # Lista de todos soquetes conectados

server_socket.listen(5)  # Quantidade de clientes que entram em espera
print(f"[*] Esperando conexoes em {ipAddress}:{SERVER_PORT}")

while True:
    r_list, w_list, x_list = select.select(lista_soquetes, [], lista_soquetes)

    for notified_socket in r_list:
        if notified_socket == server_socket:  # Nova conexao pendente
            notified_socket, endereco = server_socket.accept()
            clienteIP = endereco[0]
            print(f"[{clienteIP}] foi conectado")
            lista_soquetes.append(notified_socket)
        else:  # Nao ha conexoes novas pendentes
            correctPassword = False
            while not correctPassword:
                clientUser = receive_txt(notified_socket)
                print(f"[{clienteIP}] Usuário  = {clientUser}")

                clientPassword = receive_txt(notified_socket)
                print(f"[{clienteIP}] Senha recebida")

                if clientUser != False and clientPassword != False:
                    clientPassword = clientPassword.encode()

                    if os.path.exists("userData.csv"):
                        df = pd.read_csv("userData.csv")

                        lst = df.to_dict()
                        userDict = lst['ID']
                        hashDict = lst['HASHED_PASSWORD']

                        userValidated = False
                        for key in userDict:
                            if not userValidated:
                                if userDict[key] == clientUser:
                                    userValidated = True
                                    print(f"[{clienteIP}] Usuário encontrado na base de dados, validando senha")
                                    hashPassword = hashDict[key]
                                    hashPassword = hashPassword[2:(len(hashPassword) - 1)]
                                    hashPassword = hashPassword.encode()

                                    if bcrypt.checkpw(clientPassword, hashPassword):
                                        send_txt(notified_socket, "True")
                                        print(f"[{clienteIP}] Senha válida")
                                        correctPassword = True
                                    else:
                                        send_txt(notified_socket, "False")
                                        print(f"[{clienteIP}] Senha inválida")

                                elif not userValidated and key+1 == len(userDict):
                                    print(f"[{clienteIP}] Usuário não encontrado")
                                    send_txt(notified_socket, "False")

                    else:
                        print("Arquivo CSV contendo senhas não encontrado")
                        send_txt(notified_socket, "False")
                else:
                    send_txt(notified_socket, "False")

            clientWeight = int(receive_txt(notified_socket))
            print(f"[{clienteIP}] Peso = {clientWeight}")

            anamnese = False

            if clientWeight == 120:
                send_txt(notified_socket, "True")
                anamnese = True
            else:
                send_txt(notified_socket, "False")

            if anamnese:
                name = "Roberto"  # Adicionar nome CSV
                said = "ROBOTSTART " + name
                response = ai.respond(said)

                send_txt_indexed(client_socket=notified_socket, texto=response, serverIP=ipAddress)

                while response != "Ok, obrigada. Até logo!":
                    infoArquivo = receive_txt(notified_socket)
                    texto = process_txt(texto=infoArquivo, clienteIP=clienteIP)

                    if texto != False:
                        texto = texto.lower()

                    if texto == "até logo":
                        send_txt_indexed(client_socket=notified_socket, texto="fim de conexão", serverIP=ipAddress)
                        break

                    if texto != False:
                        try:
                            response = ai.respond(texto)
                        except:
                            response = "Desculpe, mas não consegui captar o que você disse..."

                        send_txt_indexed(client_socket=notified_socket, texto=response, serverIP=ipAddress)
                    else:
                        break

            lista_soquetes.remove(notified_socket)
