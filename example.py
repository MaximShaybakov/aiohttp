import requests


response = requests.post(f'http://127.0.0.1:8080/ads/')
headers = {'title': 'advertisements_1',
           'content': 'some content',
           'user_id': 1}

print(response.json())
