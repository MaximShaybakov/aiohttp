import requests


url = 'http://127.0.0.1:8080/users/1'

response = requests.get(url, timeout=3)
print(response.text)
