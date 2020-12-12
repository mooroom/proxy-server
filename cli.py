from socket import *
import sys
import threading

ip = str(sys.argv[1])
port = int(sys.argv[2])

def receive(clientSocket):
    while True:
        try:
            received_msg = clientSocket.recv(1024)
            print(received_msg.decode())
        except:
            break

def send(clientSocket):
    while True:
        try:
            send_msg = input('[You] ')
            clientSocket.send(send_msg.encode())
        except:
            break

    clientSocket.close()

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((ip, port))
received_enter_msg = clientSocket.recv(1024)
print(received_enter_msg.decode())

while True:
    try:
        t_receive = threading.Thread(target=receive, args=(clientSocket,))
        t_receive.daemon = True
        t_receive.start()

        t_send = threading.Thread(target=send, args=(clientSocket,))
        t_send.daemon = True
        t_send.start()

        t_receive.join()
        t_send.join()

    except KeyboardInterrupt:
        print('\nexit')
        break

clientSocket.close()