import threading
import socket
import select
import errno
import sys

HEADERLENGTH = 10
IP = "127.0.0.1"
PORT = 1234


def enviar(socket, username):
    while True:
        #escribimos el mensaje que queremos escribir
        message = input (f"{username}: ")
        
        #si existe mensaje
        if message:
            message = message.encode()
            message_header = f"{len(message) :< {HEADERLENGTH}}".encode()
            socket.send(message_header + message)



#existe el doble while true porque asi conseguimos que si no se recibe ningun mensaje 
#entrará en el except y hará un continue y después volverá al try para
#seguir recibiendo mensajes
def recibir (socket):
   while True:
        try:
            while True:
                username_header = socket.recv(HEADERLENGTH)
                if len(username_header) == 0:
                    print("connection closed by the server")
                    sys.exit()
                username_length = int(username_header.decode().strip())
                username = socket.recv(username_length).decode()
                message_header = socket.recv(HEADERLENGTH)
                message_length = int(message_header.decode().strip())
                message = socket.recv(message_length).decode()
                print(f"{username}: {message}")
        
        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

            # We just did not receive anything (importante, esto hace que sigamos recibiendo mensajes)
            continue

        except Exception as e:
            # Any other exception - something happened, exit
            print('Reading error: '.format(str(e)))
            sys.exit()

def main():
    #pedimos el username
    my_username = input("Username: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((IP,PORT))

    #vamos hacer que el metodo de recibir no bloque
    client_socket.setblocking(False)

    username_encoded = my_username.encode()

    usernameheader = f"{len(my_username):< {HEADERLENGTH}}".encode()
    client_socket.send(usernameheader + username_encoded)
    x = threading.Thread(target= enviar, args=(client_socket,my_username,))
    y = threading.Thread(target= recibir, args=(client_socket,))
    x.start()
    y.start()



if __name__ == '__main__':
    main()
