import requests

url = "https://obo-world.com:10000"

def test_data():
    service = url + "/data"
    response = requests.post(service, json={"msg": "hello"}, verify=False)
    print(response.json())
    
def ask_tchat():
    service = url + "/tchat"
    response = requests.post(service, json={"msg": "hello"}, verify=False)
    print(response.json())
    
    
test_data()
ask_tchat()