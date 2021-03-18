import requests, json
from threading import Thread
import os, time, ssl


#resp = req.get("http://localhost:8083/http://www.example.com/")
# resp = requests.get("http://localhost:8081/http://www.columbia.edu/~fdc/sample.html")
# print(resp.text)

url = 'http://localhost:8081'
payload = {
            'user'  : 'manager',
            'pswrd' : 'manager',
            'func'  : 'blklst',
            'url'   : 'www.example.com/'
}
headers = {'content-type': 'application/json'}
r = requests.post(url, data=json.dumps(payload), headers=headers)
# resp = requests.get("https://localhost:443/http://www.columbia.edu/~fdc/sample.html")
# print(resp.text)
