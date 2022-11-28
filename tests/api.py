import requests
from typing import Literal
import json
from tests.config import API_URL

session = requests.Session()


class ApiError(Exception):

    def __init__(self, status_code: int, message: dict | str):
        self.status_code = status_code
        self.message = message


def basic_request(method: Literal['get', 'post', 'patch', 'delete'], path: str, **kwargs) -> dict | str:

    method = getattr(session, method)
    response = method(f'{API_URL}/{path}', **kwargs)
    if response.status_code >= 400:
        try:
            message = response.json()
        except json.decoder.JSONDecodeError:
            message = response.text
        raise ApiError(response.status_code, message)
    return response.json()


def create_user(name: str, password: str):
    return basic_request('post', '/users/', json={'name': name, 'password': password})