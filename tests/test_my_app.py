import requests
from tests.config import API_URL
from tests import api

PASSWORD = '1234jgj#@&'

def test_root():
    response = requests.get(f'{API_URL}')
    assert response.status_code == 404

def test_create_user():
    new_user = api.create_user('Vasa', PASSWORD)
    assert 'id' in new_user