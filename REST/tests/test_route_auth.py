import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock
from src.database.model import User
from src.conf.messages import (
    INVALID_PASSWORD, INVALID_EMAIL, EMAIL_NOT_CONFIRMED, USER_EXISTS, EMAIL_CONFIRMED,
    INVALID_REFRESH_TOKEN, NOT_FOUND
)

def test_signed_user(client, user, monkeypatch):
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
    assert data["token_type"] == "bearer"


def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == EMAIL_NOT_CONFIRMED


def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == INVALID_PASSWORD


def test_login_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == INVALID_EMAIL

def test_refresh_token(client, session, user):
    current_user: User=session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed=True
    session.commit()
    response=client.post(
        "/api/auth/refresh_token" ,
        data = {"username" : user.get('email')},
    )
    assert response.status_code == 200, response.text
    data=response.json()
    assert data["token_type"] == "bearer"

def test_refresh_token_invalid(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed=True
    session.commit()

    token = "test_token"

    response = client.get(
            f"/api/auth/refresh_token/{token}",
        )
    assert response.status_code == 401, response.text
    data=response.json()
    assert data["detail"] == INVALID_REFRESH_TOKEN


def test_confirmed_email(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = False
    session.commit()

    token = "test_token"

    response = client.get(
        f"/api/auth/confirmed_email/{token}" ,
    )

    assert response.status_code == 200, response.text
    data=response.json()
    assert data["message"] == EMAIL_CONFIRMED

    updated_user: User = session.query(User).filter(User.email == user.get("email")).first()
    assert updated_user.confirmed == True


def test_already_confirmed_email(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()

    token = "test_token"

    response = client.get(
        f"/api/auth/confirmed_email/{token}",
    )

    assert response.status_code == 400, response.text
    data=response.json()
    assert data["message"] == NOT_FOUND

