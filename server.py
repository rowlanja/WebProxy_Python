import socket, sys, os, time
from cachetools import Cache, TTLCache
from _thread import *

class TTLItemCache(TTLCache):
    def __setitem__(self, key, value, cache_setitem=Cache.__setitem__, ttl=None):
        super(TTLItemCache, self).__setitem__(key, value)
        if ttl:
            link = self._TTLCache__links.get(key, None)
            if link:
                link.expire += ttl - self.ttl

try:
    this_port = input("[*] Enter the listening port: ")
    listening_port = int(os.environ.get("PORT", this_port))
except KeyboardInterrupt:
    print("\n[*] User has requested an interrupt")
    print("[*] Application Exiting.....")
    sys.exit()

max_conn = 5 #Maximum connections queues
buffer_size = 40000 #Maximum socket's buffer size
cache = TTLItemCache(maxsize=30,ttl=99000)
listOfConnections = []

def start():    #Main Program
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Initializing the socket
        s.bind(('', listening_port)) #Binding the socket to listen at the port
        s.listen(max_conn) #Start listening for connections
        print("[*] Initializing sockets........ Done!")
        print("[*] Sockets bound successfully......")
        print("[*] Server started successfully [ %d ]\n" %(listening_port))
    except Exception: #Will be executed if anything fails
        print("[*] Unable to Initialize Socket")
        sys.exit(2)

    while 1:
        conn, addr = s.accept() #Accept connection from client browser
        try:
            listOfConnections.append(conn)
            data = conn.recv(buffer_size) #Recieve client data
            start_new_thread(conn_string, (conn,data, addr)) #Starting a thread
        except KeyboardInterrupt:
            s.close()
            print("\n[*] Proxy server shutting down....")
            print("[*] Have a nice day... ")
            sys.exit(1)

def conn_string(conn, data, addr):
    # try:
    print(data.decode('latin1'))
    first_line = data.decode().split('\n')[0]
    print("fl : ", first_line)
    url = first_line
    http_pos = url.find("://") #Finding the position of ://

    if(http_pos==-1):
        temp=url
    else:
        temp = url[(http_pos+3):]

    port_pos = temp.find(":")
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)
    webserver = ""
    port = -1
    if(port_pos == -1 or webserver_pos < port_pos):
        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]
    webserver =  webserver.strip('HTTP')

    get = str('GET '+temp.replace(webserver,'')+'\n')
    host = 'Host:'+webserver+'\n\n'
    dataPackage = ((get+host).encode())
    # print(" conn : ", conn,
    #     "\n data : ", data,
    #     "\n addr : ", addr,
    #     "\n fl : ", first_line,
    #     "\n temp : ", temp,
    #     "\n port pos : " , port,
    #     "\n webserver : " , webserver,
    #     "\n decoded : ", first_line.encode(),
    #     "\n GET text : ", get,
    #     "\n Combined : ", dataPackage,
    #     "\n HOST text : ", host
    # )
    currentRequest = webserver
    proxy_server(webserver, port, conn, first_line, dataPackage, temp)
    # except Exception as e:
    #     print("exception raised : ", e)
    #     pass

def proxy_server(webserver, port, conn, addr, data, temp):
    try:
        print("Request recieved from endpoint : ", temp )

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if("usr=mngr" in temp):
                print("Recieved manager request")
                managerResp = handleManagerReq()
                conn.send(managerResp)
        else :
            urlResponse = checkCache(temp)
            if(urlResponse != None):
                print("Response recieved from cache for : ", temp )
                conn.send(urlResponse)
            else :
                s.connect((webserver, port))
                s.send(data)
                while 1:

                    reply = s.recv(buffer_size)
                    print("Response recieved from endpoint : ", temp )

                    if(reply != b'') :
                        addCache(temp, reply)
                    if(len(reply)>0):
                        conn.send(reply)
                        dar = float(len(reply))
                        dar = float(dar/1024)
                        dar = "%.3s" % (str(dar))
                        dar = "%s KB" % (dar)
                        print("[*] Request Done: %s => %s <=" % (str(addr[0]), str(dar)))

                    else:
                        break
        s.close()
        conn.close()
    except socket.error:
        s.close()
        conn.close()
        sys.exit(1)
    s.close()
    conn.close()

def checkCache(url):
    try :
        urlResponse = cache[url]
        return urlResponse
    except KeyError as e:
        print('URL not cached, retrieving from source : ', url)


def addCache(url, reply):
    print("Adding to cache : ",url)
    cache.__setitem__(url, reply)

def handleManagerReq():
    httpResponse = []
    for entry in cache:
        httpResponse.append(cache[entry])
    print("returning : ", httpResponse)
    return httpResponse
start()
