import pytest
import asyncio
from unittest import mock
from unittest.mock import MagicMock, patch, Mock
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from src.database.model import User
from src.routes.auth import signup
from src.repository import users as repository_users
from src.services.auth import auth_service

from src.conf.messages import (
    INVALID_PASSWORD, INVALID_EMAIL, EMAIL_NOT_CONFIRMED, USER_EXISTS, EMAIL_CONFIRMED,
    INVALID_REFRESH_TOKEN, NOT_FOUND, USER_CONFIRMATION, INVALID_TOKEN, ALREADY_CONFIRMED_EMAIL
)


class TestSignupUser:
    def test_successful(self, client, user, monkeypatch):
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

        response = client.post(
            "/api/auth/signup",
            json=user,
        )

        assert response.status_code == status.HTTP_201_CREATED, response.text
        data = response.json()
        assert response.json()["user"]["email"] == user.get("email")
        assert "id" in data["user"]
        assert data['detail'] == USER_CONFIRMATION

    def test_exception(self, client, user):
        response = client.post(
            "/api/auth/signup",
            json=user,
        )

        assert response.status_code == status.HTTP_409_CONFLICT, response.text
        assert response.json()["detail"] == USER_EXISTS


class TestLogin:

    def test_login_user_invalid_email(self, client, user):
        response = client.post(
            "/api/auth/login",
            data = {"username": 'invalid.email@test.com', "password": user.get('password')},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()["detail"] == INVALID_EMAIL

    def test_login_not_confirmed_email(self, client, user, session):
        response = client.post(
            "/api/auth/login",
            data = {"username": user.get('email'), "password": user.get('password')},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()["detail"] == EMAIL_NOT_CONFIRMED

    def test_login_user(self, client, session, user):
        current_user: User = session.query(User).filter(User.email == user.get('email')).first()
        current_user.confirmed = True
        session.commit()

        response = client.post(
            "/api/auth/login",
            data={"username": user.get('email'), "password": user.get('password')},
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json()["token_type"] == "bearer"

    def test_login_wrong_password(self, client, user):
        response = client.post(
            "/api/auth/login",
            data = {"username": user.get('email'), "password": "invalid_password"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()["detail"] == INVALID_PASSWORD


class TestConfirmation:
    def test_confirmed_email(self, client, session, user):
        current_user: User = session.query(User).filter(User.email == user.get('email')).first()
        current_user.confirmed = False
        session.commit()

        token = asyncio.run(auth_service.create_email_token(data = {"sub": user["email"]}))
        response = client.get(f"/api/auth/confirmed_email/{token}")

        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json() == {"message": EMAIL_CONFIRMED}


class TestRequestEmail:
    def test_request_email_already_confirmed(self, user, client, session):
        response = client.post(
            f"/api/auth/request_email",
            json = {"email": user["email"]}
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json() == {"message": ALREADY_CONFIRMED_EMAIL}

    def test_request_email_user_not_found(self, user, client, session):
        response = client.post(
            f"/api/auth/request_email",
            json = {"email": "invalid@test.com"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text
        assert response.json() == {"detail": NOT_FOUND}

    def test_request_email_successfully_confirmed(self, user, client, session):
        current_user: User = session.query(User).filter(User.email == user.get('email')).first()
        current_user.confirmed = False
        session.commit()

        response = client.post(
            f"/api/auth/request_email",
            json = {"email": user["email"]}
        )
        print(response.text)
        print(response.status_code)
        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json() == {"message": "Check your email for confirmation."}


class TestRefreshToken:
    def test_refresh_token_success(self, user, session, client):
        current_user: User = session.query(User).filter(User.email == user.get('email')).first()

        response = client.get(
            f"/api/auth/refresh_token",
            headers={"Authorization": f"Bearer {current_user.refresh_token}"}
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_invalid_token(self, user, client):
        invalid_refresh_token = asyncio.run(auth_service.create_refresh_token(
            data = {"sub": user['email']}, expires_delta=100)
        )

        response = client.get(
            f"/api/auth/refresh_token",
            headers = {"Authorization": f"Bearer {invalid_refresh_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()["detail"] == INVALID_REFRESH_TOKEN
