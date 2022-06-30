from fastapi.testclient import TestClient
from unittest.mock import patch

#import pytest
from app.main import app as meow
#from app import crud

client = TestClient(meow)



def test_get_users():
    mocked_users = [{
        'id': 1,
        'twitter_user_id': '12345'
    }]
    with patch('app.routes.users.crud.get_users', return_value = mocked_users):
        response = client.get(url='/api/users/')
        assert response.status_code == 200
        assert response.json() == [{'id': 1, 'twitter_user_id': '12345'}]



def test_post_users():
    user_request = {
        'twitter_user_id': '12345'
    }
    
    mocked_user_response = {
        'id': 1,
        'twitter_user_id': '12345'
    }
    with patch('app.routes.users.crud.create_user', return_value = mocked_user_response):
        response = client.post(url='/api/users/', json=user_request)
        print(response)
        assert response.status_code == 200
        assert response.json() == {'id': 1, 'twitter_user_id': '12345'}