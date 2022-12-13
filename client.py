from requests import request


# ---------------------- USERS ----------------------
# response = request(method='POST', url='http://127.0.0.1:8080/users/', json={'name': 'Fantomas',
#                                                                             'admin': False,
#                                                                             'password': '1234',
#                                                                             'email': 'fantomas@opa.tut'})


# response = request(method='GET', url='http://127.0.0.1:8080/users/1')

# response = request(method='PATCH', url='http://127.0.0.1:8080/users/3', json={'name': 'Boris',
#                                                                               'admin': False,
#                                                                               'password': '1234'})

# response = request(method='DELETE', url='http://127.0.0.1:8080/users/3')


# ------------------ ADVERTISEMENTS ------------------

# response = request(method='POST', url='http://127.0.0.1:8080/ads/', json={'title': 'example_2',
#                                                                           'content': 'some_content_2',
#                                                                           'user_id': 4})

# response = request(method='GET', url='http://127.0.0.1:8080/ads/2')


# response = request(method='PATCH', url='http://127.0.0.1:8080/ads/1', json={'title': 'some_title'})

response = request(method='DELETE', url='http://127.0.0.1:8080/ads/2')


print(response.json())
