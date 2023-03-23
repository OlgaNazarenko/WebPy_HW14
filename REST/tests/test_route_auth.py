import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from unittest.mock import MagicMock, Mock

from src.database.model import User
from src.routes.auth import signup
from src.repository.users import update_token
from src.services.auth import auth_service

from src.conf.messages import (
    INVALID_PASSWORD, INVALID_EMAIL, EMAIL_NOT_CONFIRMED, USER_EXISTS, EMAIL_CONFIRMED,
    INVALID_REFRESH_TOKEN, NOT_FOUND, USER_CONFIRMATION
)

def test_signup_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]
    assert data['detail'] == USER_CONFIRMATION


def test_repeat_signed_user(client, user):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == USER_EXISTS


def test_login_user(client, session, user):
    new_user = User(
        email=user["email"],
        username=user["username"],
        password=user["password"],
    )
    session.add(new_user)
    session.commit()

    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    print(data)
    assert data["token_type"] == "bearer"

def test_login_not_confirmed_email(client, user):
    # user["password"] = "123456789"
    # user["email"] = "test@example.com"
    # user["username"] = "myuser"
    user["confirmed"] = False
    print(f"{user=}")

    response = client.post(
        "/api/auth/login",
        data = {"username": user.get('email'), "password": user.get('password'), "confirmed": user.get('confirmed')},
    )

    assert response.status_code == 401
    print(response.status_code)
    assert response.json()["detail"] == EMAIL_NOT_CONFIRMED

def test_login_user_invalid_email(client, user):
    user["email"] = "invalid_email"
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == INVALID_EMAIL


def test_login_wrong_password(client, user):
    user["password"] = "invalid_password"
    user["email"] = "test@example.com"
    user["username"] = "myuser"

    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == INVALID_PASSWORD



# def test_refresh_token(user, session):
#     # First, create a user with a refresh token
#     user["password"]="invalid_password"
#     user["email"]="test@example.com"
#     user["username"]="myuser"
#
#     refresh_token = "valid_refresh_token"
#     update_token(user, refresh_token, session)
#
#     # Call the refresh_token endpoint with the valid refresh token
#     response = client.get("/refresh_token", headers={"Authorization": f"Bearer {refresh_token}"})
#
#     # Check that the response has a 200 status code and contains access and refresh tokens
#     assert response.status_code == 200
#     assert "access_token" in response.json()
#     assert "refresh_token" in response.json()
#
#     # Call the refresh_token endpoint again with the same refresh token
#     response = client.get("/refresh_token", headers={"Authorization": f"Bearer {refresh_token}"})
#
#     # Check that the response has a 401 status code, indicating the refresh token has been used
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Invalid refresh token"


# def test_refresh_token(client, user):
#     # Login to get a valid refresh token
#     login_data = {
#         'username': user['email'],
#         'password': user['password']
#     }
#     response = client.post('/login', data=login_data)
#     print('Login response status code:' , response.status_code)
#     print('Login response body:' , response.json())
#
#     data = response.json()['refresh_token']
#     # assert data ['refresh_token']
#
#     # Send the refresh token to get a new access token and refresh token
#     headers = {'Authorization': f'Bearer {refresh_token}'}
#     response = client.get('/refresh_token', headers=headers)
#
#     # Check that the response contains the new access token and refresh token
#     assert response.status_code == 200
#     assert 'access_token' in response.json()
#     assert 'refresh_token' in response.json()
#     assert response.json()['token_type'] == 'bearer'

#
# def test_refresh_token_invalid(client, session, user):
#     current_user: User = session.query(User).filter(User.email == user.get('email')).first()
#     current_user.confirmed=True
#     session.commit()
#
#     token = "test_token"
#
#     response = client.get(
#             f"/api/auth/refresh_token/{token}",
#         )
#     assert response.status_code == 401, response.text
#     data=response.json()
#     assert data["detail"] == INVALID_REFRESH_TOKEN

# def test_refresh_token(client, session, user):
#     refresh_token = auth_service.create_refresh_token(user.get('email'))
#     headers = {"Authorization": f"Bearer {refresh_token}"}
#     response = client.get('/api/auth/refresh_token', headers=headers)
#
#     assert response.status_code == 401
#     data = response.json()
#     assert data["access_token"] == ["access_token"]
#     assert data["refresh_token"] == ["refresh_token"]
#
#     assert "access_token" in response.json()
#     assert "refresh_token" in response.json()
#     assert response.json()["access_token"]
#     assert response.json()["refresh_token"]



# def test_confirmed_email(client, session, user):
#     token = "token"
#
#     response = client.get(
#         f"/api/auth/confirmed_email/{token}",
#     )
#
#     assert response.status_code == 422, response.text
#     data = response.json()
#     assert data["detail"] == NOT_FOUND
#
#     updated_user: User = session.query(User).filter(User.email == user.get("email")).first()
#     assert updated_user.confirmed == True


# def test_already_confirmed_email(client, session, user):
#     # token = "test_token"
#
#     response = client.get(
#         f"/api/auth/confirmed_email/{token}",
#     )
#
#     assert response.status_code == 422, response.text
#     data = response.json()
#     assert data["detail"] == USER_EXISTS

