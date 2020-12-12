import os, sys, threading, socket, signal

MAX_DATA_RECV = 999999
DEBUG = True
clients= []
no = 1
thread_num = 0
url_filter = 'X'
image_filter = 'X'

def main():

    if(len(sys.argv) < 2):
        print('Please enter port number.')
        sys.exit(1)
    else:
        port = int(sys.argv[1])
        print('Starting proxy server on port {}'.format(port))

    host = 'localhost'

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(20)


    while True:
        try:
            conn, client_addr = s.accept()

        except KeyboardInterrupt:
            break

        clients.append(conn)
        t = threading.Thread(target=proxy_thread, args=(conn, client_addr))
        t.setDaemon(True)
        t.start()

    print('\n=======================')
    print('Proxy server terminated.')
    s.close()
    sys.exit(1)

def proxy_thread(conn, client_addr):
    request = conn.recv(MAX_DATA_RECV)

    global thread_num
    global no

    global image_filter
    global url_filter

    thread_num += 1

    # print("-------------------")
    # print("REQUEST: ")
    # print(request)
    # print("-------------------")

    first_line = request.decode().split('\r\n')[0]

    try:
        url = first_line.split('GET ')[1]
    except:
        print('URL not found')
        sys.exit(1)

    #######################
    #url filter
    if 'yonsei' in url:
        url_filter = 'O'
    else:
        url_filter = 'X'

    #image filter
    if '?image_off' in url:
        image_filter = 'O'
        url.split('?image_off')[0]
    elif 'image_on' in url:
        image_filter = 'X'
        url.split('?image_on')[0]
    else:
        image_filter = 'O'
    #######################

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

    # print("WEBSERVER:")
    # print(webserver)
    # print("-------------------")

    print('-----------------------------------------------')
    print('{}  [Conn:    {}/  {}]'.format(no, thread_num, len(clients)))
    print('[ {} ] URL filter | [ {} ] Image filter\n'.format(url_filter, image_filter))
    print('[CLI connected to {}:{}]'.format(client_addr[0], client_addr[1]))
    print('[CLI ==> PRX --- SRV]')

    no += 1

    #get request message
    req_messages = request.decode().split('\r\n')
    get_message = req_messages[0]
    user_agent_message = ''

    for i in req_messages:
        if 'User-Agent' in i:
            user_agent_message = i.split('User-Agent: ')[1]
    ####################

    print('\t> {}'.format(get_message))
    print('\t> {}'.format(user_agent_message))


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    if url_filter == 'O':
        webserver = 'www.linuxhowtos.org'

    s.connect((webserver, port))
    print('[SRV connected to {}:{}]'.format(webserver, port))

    s.sendall(request)
    print('[CLI --- PRX ==> SRV]')
    print('\t> {}'.format(get_message))
    print('\t> {}'.format(user_agent_message))

    while 1:
        data = s.recv(MAX_DATA_RECV)
        # print("DATA:")
        
        img_flag = False
        splited = data.split(b'\r\n\r\n')
        header = splited[0]
        # print('===header=====')
        # print(header)
        # print('==========')

        res_status = ''
        res_type = ''
        res_size = ''

        header_exits = False

        try:
            decoded_header = header.decode()
            if image_filter == 'O':
                if 'image/' in decoded_header:
                    img_flag = True

            splited_header = decoded_header.split('\r\n')
            res_status = splited_header[0].split('HTTP/1.1 ')[1]

            for i in splited_header:
                if 'Content-Type' in i:
                    res_type = i.split('Content-Type: ')[1]
                if 'Content-Length' in i:
                    res_size = i.split('Content-Length: ')[1]

            print('[CLI --- PRX <== SRV]')
            print('\t> {}'.format(res_status)) 
            print('\t> {} {}bytes'.format(res_type, res_size))

            header_exits = True
        except:
            pass 

        

        if(len(data) > 0 and img_flag == False) :
            if header_exits:
                print('[CLI <== PRX --- SRV]')
                print('\t> {}'.format(res_status)) 
                print('\t> {} {}bytes'.format(res_type, res_size)) 
            conn.send(data)
        else:
            break

    conn.close()
    clients.remove(conn)
    print('[CLI disconnected]')

    s.close()
    print('[SRV disconnected]')


if __name__ == '__main__':
    main()
 

