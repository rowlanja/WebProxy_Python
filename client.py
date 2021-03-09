import requests as req
from threading import Thread
import os, time, ssl

hostname = 'www.python.org'
# PROTOCOL_TLS_CLIENT requires valid cert chain and hostname
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations('path/to/cabundle.pem')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(ssock.version())
#resp = req.get("http://localhost:8083/http://www.example.com/")
os.environ['NO_PROXY'] = '127.0.0.1'
resp = req.get("https://localhost:8082/https://www.example.com/")
print(resp.text)

time.sleep(2)

# resp = req.get("http://localhost:8081/usr=mngr&pswrd=mngr")
# print(resp.text)
