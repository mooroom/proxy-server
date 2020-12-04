import os, sys, threading, socket

MAX_DATA_RECV = 999999
DEBUG = True
BLOCKED = ["yonsei"]

def main():
    if(len(sys.argv) < 2):
        print("No port given, using: 8080")
        port = 8080
    else:
        port = int(sys.argv[1])

    host = 'localhost'
    print("Proxy Server Running on {} : {}".format(host, port))

    # try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(50)

    # except socket.error:
    #     if s:
    #         s.close()

    #     print("Could not open socket: ")
    #     sys.exit(1)

    while 1:
        conn, client_addr = s.accept()
        t = threading.Thread(target=proxy_thread, args=(conn, client_addr))
        t.setDaemon(True)
        t.start()

    s.close()

def printout(type, request, address):
    if("Block" in type or "Blacklist" in type):
        colornum = 91
    elif("Request" in type):
        colornum = 92
    elif("Reset" in type):
        colornum = 93

    print("\033[" + colornum + "m" + address[0] + "\t" + type + "\t" + request + "\033[0m")

def proxy_thread(conn, client_addr):
    request = conn.recv(MAX_DATA_RECV)
    print("'''''''''''''")
    print("connection:")
    print(conn)
    print("'''''''''''''")
    print("request")
    print(request)
    print("'''''''''''''")

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

    print("'''''''''''''")
    print(webserver)
    print("'''''''''''''")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((webserver, port))
    s.sendall(request)

    while 1:
        data = s.recv(MAX_DATA_RECV)
        print("DATA: " + data.decode())

        if(len(data) > 0) :
            conn.send(data)
        else:
            break

    s.close()
    conn.close()

if __name__ == '__main__':
    main()
 

