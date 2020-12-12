from socket import *
import threading
import sys

host = 'localhost'
port = int(sys.argv[1])
img_filter = 'X'
url_filter = 'X'
no = 0
conn_no = 0
clients = []

print('Starting proxy server on port {}'.format(port))

s_proxy_socket = socket(AF_INET, SOCK_STREAM)
s_proxy_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s_proxy_socket.bind((host, port))
s_proxy_socket.listen(20)

def destination_info(first_line):
    url = ''
    try:
        url = first_line.split()[1]
    except:
        print('URL not found.')
        pass

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

    return (url, webserver, port)

def proxy_thread(conn, conn_no, addr):
    global img_filter
    global url_filter
    global no

    request = conn.recv(1024)

    first_line = request.decode().split('\r\n')[0]
    (url, webserver, port) = destination_info(first_line)

    if '?image_off' in url:
        img_filter = 'O'
    elif '?image_on' in url:
        img_filter = 'X'

    if 'yonsei' in url:
        req_decoded_split = request.decode().split('\r\n')
        newGET = 'GET http://www.linuxhowtos.org/ HTTP/1.1'
        newHOST = 'Host: www.linuxhowtos.org'
        req_decoded_split[0] = newGET
        req_decoded_split[1] = newHOST
        new_req = '\r\n'.join(req_decoded_split).encode()
        request = new_req
        first_line = request.decode().split('\r\n')[0]
        (url, webserver, port) = destination_info(first_line)
        url_filter = 'O'
    else:
        url_filter = 'X'

    #get request message
    req_messages = request.decode().split('\r\n')
    get_message = req_messages[0]
    user_agent_message = ''

    for i in req_messages:
        if 'User-Agent' in i:
            user_agent_message = i.split('User-Agent: ')[1]
    ####################

    no += 1

    print('-----------------------------------------------')
    print('{}  [Conn:    {}/  {}]'.format(no, conn_no, len(clients)))
    print('[ {} ] URL filter | [ {} ] Image filter\n'.format(url_filter, img_filter))
    print('[CLI connected to {}:{}]'.format(addr[0], addr[1]))
    print('[CLI ==> PRX --- SRV]')
    print('  > {}'.format(get_message))
    print('  > {}'.format(user_agent_message))

    c_proxy_socket = socket(AF_INET, SOCK_STREAM)

    c_proxy_socket.connect((webserver, port))
    print('[SRV connected to {}:{}]'.format(webserver, port))

    c_proxy_socket.sendall(request)
    print('[CLI --- PRX ==> SRV]')
    print('  > {}'.format(get_message))
    print('  > {}'.format(user_agent_message))

    while True:
        data = c_proxy_socket.recv(4096)
        header = ''
        res_status = ''
        res_type = ''
        res_size = ''
        header_exits = False
        
        try:
            header = data.split(b'\r\n\r\n')[0].decode()
            splited_header = header.split('\r\n')
            res_status = splited_header[0].split('HTTP/1.1 ')[1]

            for i in splited_header:
                if 'Content-Type' in i:
                    res_type = i.split('Content-Type: ')[1]
                if 'Content-Length' in i:
                    res_size = i.split('Content-Length: ')[1]

            print('[CLI --- PRX <== SRV]')
            print('  > {}'.format(res_status)) 
            print('  > {} {}bytes'.format(res_type, res_size))

            header_exits = True
        except:
            pass

        if img_filter == 'O':
            if 'image/' in header:
                break

        if len(data) > 0:
            conn.send(data)
            if header_exits:
                print('[CLI <== PRX --- SRV]')
                print('  > {}'.format(res_status)) 
                print('  > {} {}bytes'.format(res_type, res_size)) 
        else:
            break

    cli_copy = clients
    for i in cli_copy:
        if conn in i:
            clients.remove(i)
            
    conn.close()
    print('[CLI disconnected]')

    c_proxy_socket.close()
    print('[SRV disconnected]')

#############################
#main loop
while True:
    try:
        conn, addr = s_proxy_socket.accept()
    except KeyboardInterrupt:
        for client in clients:
            client[0].close()
        s_proxy_socket.close()
        print('\nTerminate Proxy Sever.')
        break

    conn_no += 1
    conn_info = (conn, conn_no)
    clients.append(conn_info)

    t = threading.Thread(target=proxy_thread, args=(conn, conn_no, addr))
    t.daemon = True
    t.start()


