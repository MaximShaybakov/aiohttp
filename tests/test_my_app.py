import requests
import pytest
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
    assert user['name'] == root_user['name']


def test_user_non_existed():
    with pytest.raises(api.ApiError) as err_info:
        api.get_user(999999)
    assert err_info.value.status_code == 404
    assert err_info.value.message == {'status': 'error', 'message': 'User not found'}


def test_patch_user(new_user):
    response = api.patch_user(new_user['id'], patch={'name': 'vasja',
                                                     'admin': False,
                                                     'password': '1234',
                                                     'email': None})
    assert response == {'status': 'success'}
    user = api.get_user(new_user['id'])
    assert user['name'] == 'vasja'


def test_patch_user_non_existed(new_user):
    pass


def test_delete_user(new_user: int):
    response = api.delete_user(new_user['id'])
    assert response == {'status': 'delete'}
    with pytest.raises(api.ApiError) as err_info:
        api.get_user(new_user['id'])
    assert err_info.value.status_code == 404
    assert err_info.value.message == {'status': 'error', 'message': 'User not found'}


def test_delete_user_non_existed(new_user: int):
    pass
