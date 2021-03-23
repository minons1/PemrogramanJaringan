import socket,sys

server_address = 'localhost', 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(server_address)
server_socket.listen(5)

try:
    while True:
        print("Server listened to port 5000")
        client_socket, client_address = server_socket.accept()
        print(client_socket, client_address)

        data = client_socket.recv(1024)
        print(data)

        client_socket.close()

except KeyboardInterrupt:
    server_socket.close()
    sys.exit(0)