import requests as req
from threading import Thread
import os, time, ssl


#resp = req.get("http://localhost:8083/http://www.example.com/")
resp = req.get("http://localhost:8081/https://www.example.com/")
print(resp.text)


# resp = req.get("http://localhost:8081/usr=mngr&pswrd=mngr")
# print(resp.text)
