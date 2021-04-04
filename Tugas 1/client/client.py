import socket
import sys

success_msg = (bytes('File sent successfully', 'utf-8'))
failed_msg = (bytes('File not found', 'utf-8'))

# create socket and connect to server
# server_address = ('192.168.100.186', 5000)
server_address = ('192.168.43.225', 5000)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

try:
    while True:
        message = sys.stdin.readline()
        # melakukan parsing untuk mendapatkan nama file
        message_split = message.split(' ',1)
        filename = message_split[1].rstrip("\n")

        # mengirimkan request filename ke server
        client_socket.send(bytes(message, 'utf-8'))
        recv_data = client_socket.recv(1024)

        # melakukan parsing untuk mendapatkan message header
        message_header = recv_data.split('\n'.encode(),4)
        
        if len(message_header) > 3:
            for i in range (4):
                print(message_header[i])
                
        # jika file tidak ada atau error, maka koneksi akan ditutup
        elif message_header[0].decode('utf-8') == 'Error':
            print("Terjadi kelasalahan pada input ataupun file")
            continue
        
        # membuat file dan mengisi data kedalam file
        with open(filename, 'wb') as file:
            # Panjang pesan untuk membatasi loop recv sesuai ukuran file
            msg_len = message_header[1].decode('utf-8').split(" ")
            file_len = (int(msg_len[1][:-1])//1024) + 1
            print ('File dibuat')

            # mengirimkan file yang masuk ke recv_data (untuk memenuhi slot 1024 bytes sebelum
            # masuk ke variabel selanjutnya (data))
            # file.write(message_header[4])
            
            while file_len:
                print('Menerima data...')
                data = client_socket.recv(1024)
                file.write(data)
                file_len-=1

        ## INTERRUPT DENGAN KEYBOARD UNTUK MENGHENTIKAN PROSES

        # file telah diterima
        print("File telah diterima\n")

except KeyboardInterrupt:
    client_socket.close()
    sys.exit(0)