import requests
from tests.config import API_URL
from tests import api


def test_root():
    response = requests.get(f'{API_URL}')
    assert response.status_code == 404


def test_create_user():
    new_user = api.create_user('user_1', True, 'my_first_password', 'user@mail.ru')
    assert 'id' in new_user


def test_get_user(root_user):
    user = api.get_user(root_user['id'])
    print(user)
    assert user['name'] == root_user['name']
