import os, sys, threading, socket, signal

MAX_DATA_RECV = 999999
DEBUG = True
BLOCKED = ["yonsei"]
clients = []

def main():

    if(len(sys.argv) < 2):
        print("No port given, using: 8080")
        port = 8080
    else:
        port = int(sys.argv[1])

    host = 'localhost'
    print("Proxy Server Running on {} : {}".format(host, port))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(10)


    while True:
        try:
            conn, client_addr = s.accept()

        except KeyboardInterrupt:
            for client in clients:
                client.close()
            print('\nexit')
            break
        
        clients.append(conn)
        t = threading.Thread(target=proxy_thread, args=(conn, client_addr))
        t.setDaemon(True)
        t.start()

    s.close()

def printout(type, request, address):
    colornum = 0
    if("Block" in type or "Blacklist" in type):
        colornum = 91
    elif("Request" in type):
        colornum = 92
    elif("Reset" in type):
        colornum = 93

    print("\033[ {} m {} \t {} \t {} \033[0m".format(colornum, address[0], type, request))

def proxy_thread(conn, client_addr):
    request = conn.recv(MAX_DATA_RECV)

    print("CONNECTION: ")
    print(conn)
    print("-------------------")
    print("REQUEST: ")
    reqsplited = request.split()
    for i in reqsplited:
        print(i.decode('utf-8'))
    print("-------------------")

    first_line = request.decode().split('\n')[0]

    url = first_line.split(' ')[1]

    for i in range(0, len(BLOCKED)):
        if BLOCKED[i] in url:
            printout("Blacklisted", first_line, client_addr)
            conn.close()
            sys.exit(1)

    http_pos = url.find("://")
    if(http_pos == -1):
        temp = url
    else:
        temp = url[(http_pos + 3):]

    port_pos = temp.find(":")

    webserver_pos = temp.find("/")
    if(webserver_pos == -1):
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if(port_pos == -1 or webserver_pos < port_pos):
        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos] 

    print("WEBSERVER:")
    print(webserver)
    print("-------------------")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
    s.connect((webserver, port))
    s.sendall(request)

    while 1:
        data = s.recv(MAX_DATA_RECV)
        print("DATA:")
        # decoded = data.decode()
        splited = data.split()
        for i in splited:
            print(i.decode('utf-16'))
        print("-------------------")

        if(len(data) > 0) :
            conn.send(data)
        elif socket.error or KeyboardInterrupt:
            break

    conn.close()
    s.close()
    
    print("---------Exit---------")
    sys.exit(1)


if __name__ == '__main__':
    main()
 

