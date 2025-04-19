import requests

res = requests.post("http://127.0.0.1:3000/api/courses/efjv", {"name": "Golang"}, )
print(res.json())
