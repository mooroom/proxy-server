from socket import *
import threading
import sys

ip = str(sys.argv[1])
port = int(sys.argv[2])

print('Chat Server started on port %d'%port)
clients = []

def send_msg(msg, conn):
    print(msg)
    for client in clients:
        if client != conn:
            try:
                client.send(msg.encode())
            except Exception as e:
                print(e)

def send_all(msg):
    print(msg)
    for client in clients:
        try:
            client.send(msg.encode())
        except Exception as e:
            print(e)

def receive(connectionSocket, addr):
    user_flag = 'user' if len(clients) < 2 else 'users'
    enter_msg = '\n> New user %s:%s entered (%d %s online)'%(addr[0], addr[1], len(clients), user_flag)
    send_msg(enter_msg, connectionSocket)
    enter_msg2 = '\n> Connected to the chat server (%d %s online)'%(len(clients), user_flag)
    connectionSocket.send(enter_msg2.encode())
    while True:
        data = connectionSocket.recv(1024)
        if data:
            string = data.decode()
            user_msg = "[%s:%s] %s"%(addr[0], addr[1], string)
            send_msg(user_msg, connectionSocket)
        else:
            clients.remove(connectionSocket)
            user_flag = 'user' if len(clients) < 2 else 'users'
            leave_msg = '\n< The user %s:%s left (%d %s online)'%(addr[0], addr[1], len(clients), user_flag)
            send_all(leave_msg)
            break
    connectionSocket.close()

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind((ip, port))
serverSocket.listen(5)            

while True:
    try:
        connectionSocket, addr = serverSocket.accept()
    except KeyboardInterrupt:
        for client in clients:
            client.close()
        serverSocket.close()
        print('\nexit')
        break

    clients.append(connectionSocket)

    t = threading.Thread(target=receive, args=(connectionSocket, addr))
    t.daemon = True
    t.start()