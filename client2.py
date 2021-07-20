import threading
import socket
import select
import errno
import sys
HEADERLENGTH = 10
IP = "127.0.0.1"
PORT = 1234
#pedimos el username
my_username = input("Username: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((IP,PORT))

#vamos hacer que el metodo de recivir no bloque
client_socket.setblocking(False)

username_encoded = my_username.encode()

usernameheader = f"{len(my_username):< {HEADERLENGTH}}".encode()
client_socket.send(usernameheader + username_encoded)

def enviar(socket):
    while True:
        #escribimos el mensaje que queremos escribir
        message = input (f"{my_username}: ")
        
        #si existe mensaje
        if message:
            message = message.encode()
            message_header = f"{len(message) :< {HEADERLENGTH}}".encode()
            socket.send(message_header + message)




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

            # We just did not receive anything
            continue

        except Exception as e:
            # Any other exception - something happened, exit
            print('Reading error: '.format(str(e)))
            sys.exit()


x = threading.Thread(target= enviar, args=(client_socket,), daemon= True)
y = threading.Thread(target= recibir, args=(client_socket,), daemon= True)
x.start()
y.start()