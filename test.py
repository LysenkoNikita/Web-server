import requests
import json

def getUsers():
    r = requests.get("https://127.0.0.1:8000/users", verify=False)
    return r.json()

print(getUsers())