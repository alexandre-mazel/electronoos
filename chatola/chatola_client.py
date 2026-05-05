import requests

url = "https://obo-world.com:5000/data"

response = requests.post(url, json={"msg": "hello"}, verify=False)
print(response.json())