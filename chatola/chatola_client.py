import requests

url = "https://obo-world.com:10000/data"

response = requests.post(url, json={"msg": "hello"}, verify=False)
print(response.json())