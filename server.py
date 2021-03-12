import socket, sys, os, time, json, time, ssl
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
buffer_size = 16000 #Maximum socket's buffer size
cache = TTLItemCache(maxsize=30,ttl=99000) #Initializing my TTL cache
blacklist = []  # Intializing my blacklisted URLS

def start():    #Main Program
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Initializing the socket
        s.bind(('', listening_port)) #Binding the socket to listen at the port
        s.listen(max_conn) #Start listening for connections
    except Exception: #Will be executed if anything fails
        sys.exit(2)

    threadID = 0
    while 1:
        conn, addr = s.accept() #Accept connection from client browser
        try:
            data = conn.recv(buffer_size) #Recieve client data
            decodeData = data.decode().split('\n')
            req = decodeData[0]
            if '"user": "manager", "pswrd": "manager"' in data.decode() : #IF WE RECIEVE A PROXY MANAGEMENT REQUEST
                start_new_thread(handleManagerReq, (decodeData,threadID))
                threadID += 1
            else :
                if not "favicon" in req :   #IF WE RECIEVE A NORMAL REQUEST
                    start_new_thread(conn_string, (conn,data, addr, threadID, time.time()))
                    threadID += 1
        except KeyboardInterrupt:
            s.close()
            print("\n[*] Proxy server shutting down....")
            print("[*] Have a nice day... ")
            sys.exit(1)

def conn_string(conn, data, addr, threadID, startTime):
    first_line = data.decode().split('\n')[0]
    url = first_line
    http_pos = url.find("://")

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
    if "/http:/" in first_line :
        get = str('GET '+temp.replace(webserver,'')+'\n')
        host = 'Host: '+webserver+'\n\n'
        dataPackage = ((get+host).encode())
    else :
        get = str('GET '+temp.replace(webserver,'')+'\n')
        host = 'Host: '+webserver[4:]
        dataPackage = (get+host+"\r\nConnection: close\r\n\r\n").encode()
        print("dp : ", dataPackage)
    fullURL = temp.replace('/ HTTP/1.1', '').strip()  # remove HTTP version from URL
    # print("the bitch says : \n",
    # "fullurl : ", fullURL,
    # "get : ", get,
    # "temp : ", temp,
    # "url  : ", url,
    # "ws : ", webserver,
    # "get : ", get,
    # "host : ", host,
    # "first : ", first_line
    # )

    if fullURL not in blacklist:
        proxy_server(webserver, port, conn, first_line, dataPackage, first_line, threadID, startTime)
    else :
        print("[*] Request rejected, blacklisted URL")
        while True:
            rawString = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+blacklistHTML+"\n"
            html = rawString.encode('utf-8')
            conn.send(html)
            conn.close()
            break;


def proxy_server(webserver, port, conn, addr, data, temp, threadID, startTime):
    fullReply = bytearray()
    timeDifference = 0.0
    try:
        print("[*] Request recieved from endpoint : " , webserver, " handled by thread : ", threadID)
        s= socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        urlResponse = checkCache(temp)
        if(urlResponse != None):        # CHECK IF THE URL IS CACHED BEFORE CONSIDERING FETCHING IT
            conn.send(urlResponse)
            dar = float(len(urlResponse))
            dar = float(dar/1024)
            dar = "%.3s" % (str(dar))
            dar = "%s KB" % (dar)
            print("[*] Saved bandwidth : => %s <=" % (str(dar)))
            print("[*] Request Processed in : => %s seconds <= " % (str(time.time()-startTime)))
            print("----------- SENDING CACHED RESPONSE FINISHED -------------\n\n")
        else :
            if "/https:" in temp :
                print("[*] opening socket on SSL port 443")
                context = ssl.SSLContext();
                context.verify_mode     = ssl.CERT_REQUIRED;
                context.check_hostname  = True;
                context.load_default_certs();
                webserver = webserver[4:]
                print("webserver : ", webserver, ' data : ', data)
                s.connect((webserver, 443));                 # Connect to host
                # s = ssl.wrap_socket(s, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1)
                # s.sendall(b'GET / HTTP/1.1\r\nHost: github.com\r\nConnection: close\r\n\r\n')

                # s.connect(('github.com', 443))
                s = ssl.wrap_socket(s, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)
                s.sendall(data)

                while True:
                    new = s.recv(buffer_size)
                    if(len(new)>0):
                        fullReply += new
                        timeDifference = (time.time()-startTime)
                        conn.sendall(new)
                    else:
                      break
                dar = float(len(fullReply))
                dar = float(dar/1024)
                dar = "%.3s" % (str(dar))
                dar = "%s KB" % (dar)
                print("[*] Request relayed to client : => %s <=" % (str(dar)))
                print("[*] Request Processed in : => %s seconds <=" % timeDifference)
                print("----------- SENDING FETCHED RESPONSE FINISHED -------------\n\n")
                addCache(temp, fullReply)
            else :
                print("http")
                s.settimeout(2)
                s.connect((webserver, port))
                s.send(data)
                while 1:
                    reply = s.recv(buffer_size)
                    if(len(reply)>0):
                        conn.sendall(reply)
                        fullReply += reply
                        timeDifference = (time.time()-startTime)
                    else:
                        break

    except (BlockingIOError, socket.timeout, OSError, ssl.SSLError):
        print("[*] Caching " + temp)
        addCache(temp, fullReply)
        dar = float(len(fullReply))
        dar = float(dar/1024)
        dar = "%.3s" % (str(dar))
        dar = "%s KB" % (dar)
        print("[*] Request relayed to client : => %s <=" % (str(dar)))
        print("[*] Request Processed in : => %s seconds <=" % timeDifference)
        print("----------- SENDING FETCHED RESPONSE FINISHED -------------\n\n")
        pass
    except socket.error:
        print("Error occured in thread")
        s.close()
        conn.close()
        sys.exit(1)
    except Exception as e:
        print("Undiagnosed error : ", e)
    s.close()
    conn.close()

def checkCache(url):
    try :
        urlResponse = cache[url]
        print("[*] Found in cache : ", url)
        return urlResponse
    except KeyError as e:
        print('[*] URL not cached, retrieving from source : ', url)


def addCache(url, reply):
    cache.__setitem__(url, reply)

def handleManagerReq(req, threadID):

    print("[*] MANAGER CONNECTION HANDLED BY : ",threadID)
    payload = req[len(req)-1]   # extracts string containing json payload
    json_acceptable_payload = payload.replace("'", "\"") # creates json payload
    json_payload = json.loads(json_acceptable_payload)
    print('json : ', json_payload)
    if json_payload["func"] == "blklst":
        blacklist.append(json_payload["url"])
        print('[*] blacklist updated, ADDED : ', json_payload["url"])
    if json_payload["func"] == "rmblk":
        blacklist.remove(json_payload["url"])
        print('[*] blacklist updated, REMOVED : ', json_payload["url"])
    if json_payload["func"] == "usrBan":
        blacklist.remove(json_payload["url"])
        print('[*] blacklist updated, REMOVED : ', json_payload["url"])

blacklistHTML = """
    <!doctype html>
    <html> <head> <title>BLACKLISTED Domain</title>
        <meta charset="utf-8" />
        <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style type="text/css">
        body {
            background-color: #f0f0f2;
            margin: 0;
            padding: 0;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;}
        div {
            width: 600px;
            margin: 5em auto;
            padding: 2em;
            background-color: #fdfdff;
            border-radius: 0.5em;
            box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);
        }
        a:link, a:visited {
            color: #38488f;
            text-decoration: none;
        }
        @media (max-width: 700px) {
            div {
                margin: 0 auto;
                width: auto;
            }
        }
        </style>
    </head>
    <body>
    <div>
        <h1>BLACKLISTED Domain</h1>
        <p>This domain is BLACKLISTED. You need to contact the proxy manager to enquire about access to this endpoint</p>
        <p><a ">More information...</a></p>"""

start()
