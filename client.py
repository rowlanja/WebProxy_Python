import requests, json
from threading import Thread
import os, time, ssl


#resp = req.get("http://localhost:8083/http://www.example.com/")
#resp = req.get("http://localhost:8081/https://www.example.com/")
#print(resp.text)

url = 'http://localhost:8084'
payload = {
            'user'  : 'manager',
            'pswrd' : 'manager',
            'func'  : 'blklst',
            'url'   : 'www.example.com'
}
headers = {'content-type': 'application/json'}

r = requests.post(url, data=json.dumps(payload), headers=headers)
# resp = req.get("http://localhost:8081/usr=mngr&pswrd=mngr")
print(resp.text)
