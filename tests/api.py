import requests
from typing import Literal
import json
from tests.config import API_URL

session = requests.Session()


class ApiError(Exception):

    def __init__(self, status_code: int, message: dict | str):
        self.status_code = status_code
        self.message = message


def basic_request(method: Literal['get', 'post', 'patch', 'delete'], path: str, **kwargs) -> dict:
    method = getattr(session, method)
    response = method(f'{API_URL}{path}', **kwargs)
    if response.status_code >= 400:
        try:
            message = response.json()
        except json.decoder.JSONDecodeError:
            message = response.text
        raise ApiError(response.status_code, message)
    return response.json()


def create_user(name: str, admin: bool, password: str, email: str):
    return basic_request('post', '/users/', json={'name': name,
                                                  'admin': admin,
                                                  'password': password,
                                                  'email': email})


def get_user(user_id: int):
    return basic_request('get', f'/users/{user_id}')


def patch_user(user_id: int, patch: dict):
    return basic_request('patch', f'/users/{user_id}', json=patch)


def delete_user(user_id: int, token: str):
    return basic_request('delete', f'/users/{user_id}', headers={'token': token})


def login(name: str, password: str):
    return basic_request('post', '/login', json={'name': name, 'password': password})
