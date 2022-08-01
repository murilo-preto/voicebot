import socket
import select

# Iniciar constantes
SERVER_HOST = "192.168.0.11"
SERVER_PORT = 5001
SEPARADOR = "<SEPARATOR>"  # Separador de texto auxiliar
TAMANHO_BUFFER = 4096  # Qtd de bytes a serem recebidos por scan
NOME_ARQUIVO = "audio.mp3"  # Nome do arquivo de audio
HEADER_LEN = 10  # Tamanho header da msg


# Funcoes
def recebertxt(client_socket):  # Receber texto, cliente que o envia como argumento
    try:
        tamanhotxt = client_socket.recv(HEADER_LEN).decode()
        tamanhotxt = int(tamanhotxt.strip())
        txt = client_socket.recv(tamanhotxt).decode()
        return txt
    except:
        return False


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
            infoArquivo = recebertxt(notified_socket)

            if infoArquivo is False:  # recebertxt retornou falso: cliente fechou conexao
                lista_soquetes.remove(notified_socket)
            else:  # indice recebido valido
                tipoArquivo, tamanhoArquivo = infoArquivo.split(SEPARADOR)
                tamanhoArquivo = int(tamanhoArquivo)

                if tipoArquivo == "audio":
                    with open(NOME_ARQUIVO, "wb") as f:  # Baixar audio encapsulado
                        while True:
                            bytesLidos = notified_socket.recv(TAMANHO_BUFFER)
                            if not bytesLidos:
                                break
                            f.write(bytesLidos)
                    # audio baixado como "audio.mp3"
                    # pendente: transcrever audio baixado em texto

                elif tipoArquivo == "texto":
                    texto = recebertxt(notified_socket)  # Receber texto
                    print(texto)

                # Processar texto, guardar info, enviar resposta ao soquete

    for notified_socket in x_list:
        lista_soquetes.remove(notified_socket)
