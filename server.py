import socket
import select

HEADERLENGTH = 10
IP = "127.0.0.1"
PORT = 1234

#definimos la funcion que dado un socket nos dirá si hay algun mensaje que ha enviado

def recive_message(client_socket):
    try:
        #recibimos el tamaño del mensaje 
        message_header = client_socket.recv(HEADERLENGTH)
        #si no tiene header
        if len(message_header) == 0:
            return False
        #en caso contrario tenemos el tamaño del mensaje
        message_length = int(message_header.decode().strip())
        #devolvemos un diccionario que contiene el tamaño y el contenido
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        return False

def main():
    #creamos server_socket

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #esto sirve que en la terminal no el error "address already in use"
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((IP,PORT))

    server_socket.listen()

    #creamos la lista de sockets que se conectaran
    socket_list = [server_socket]
    #creamos un diccionario de clientes, por cada socket, nos guardaremos su username
    clients = {}


    #CUERPO DEL SERVER


    while True:



        #crearemos 3 listas que son los sockets que tienen que ser leidos, escritos y sockets que tienen un error
        # la funcion select
        read_sockets, _, exception_sockets = select.select(socket_list,[], socket_list)

        #tenemos que ir por cada socket y leerlo
        for individual_socket in read_sockets:
            #si el socket es el principal, mirara si hay alguna conexion en vivo
            if individual_socket == server_socket:
                clients_socket, client_address = server_socket.accept()
                #el usuario la primera palabra que diga debe de ser el su username
                user = recive_message(clients_socket)

                #metemos el socket del cliente y asociamos a cada client_socket pues su username
                socket_list.append(clients_socket)
                clients[clients_socket] = user
            
                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
            else:

                #si no es del servidor significa que alguien ha enviado un mensaje
                message = recive_message(individual_socket)

                #si el mensaje es vacío(el usuario se ha desconectado)
                if message == 0:
                    print('Closed connection from: {}'.format(clients[individual_socket]['data'].decode()))
                    socket_list.remove(individual_socket)
                    del clients[individual_socket]
                    continue
                user = clients[individual_socket]
                print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

                for client_socket in clients:
                    if client_socket != individual_socket:
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

        #quitamos los sockets que tengan algo mal
        for individual_socket in exception_sockets:
            socket_list.remove(individual_socket)
            del clients[individual_socket]

if __name__ == '__main__':
    main()
