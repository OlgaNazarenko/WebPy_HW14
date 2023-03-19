import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock, patch

import pytest

from src.database.model import User
from src.services.auth import auth_service
from src.conf.messages import (
    NOT_FOUND
)

@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_create_contact(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/contacts",
            json={
                "name": "Isana",
                "surname": "Gratis",
                "email": "test@email.com",
                "mobile": "111111111",
                "date_of_birth": "2000-03-21"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["name"] == "Isana"
        assert data["surname"] == "Gratis"
        assert data["email"] == "test@email.com"
        assert data["mobile"] == "111111111"
        assert data["date_of_birth"] == "2000-03-21"
        assert "id" in data


def test_create_contact_not_found(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_contacts(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["name"] == "Isana"
        assert "id" in data[0]

def test_get_contact(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["name"] == "Isana"
        assert "id" in data

def test_get_contact_not_found(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_update_contact(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            "/api/contacts/1",
            json={
                "name": "Composition",
                "surname": "Norcom",
                "email": "test2@email.com",
                "mobile": "222222222",
                "date_of_birth": "2000-03-25"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["name"] == "Composition"
        assert data["surname"] == "Norcom"
        assert data["email"] == "test2@email.com"
        assert data["mobile"] == "222222222"
        assert data["date_of_birth"] == "2000-03-25"
        assert "id" in data


def test_update_contact_not_found(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            "/api/contacts/1",
            json={
                "name": "Composition",
                "surname": "Norcom",
                "email": "test2@email.com",
                "mobile": "222222222",
                "date_of_birth": "2000-03-25"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


@pytest.mark.parametrize("search_term, expected_count", [
    ("Composition", 1),
    ("Norcom", 1),
    ("test2@email.com", 1),
    ("foo", 0)
])

def test_get_contacts_by_query(client, token, search_term, expected_count):
    with patch.object(auth_service, "redis") as r_mock:
        r_mock.get.return_value = None
        response=client.get(
            "/api/contacts/by_choice?query={search_term}" ,
            headers = {"Authorization" : f"Bearer {token}"}
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == search_params["result"]

def test_get_contacts_birthdays(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/birthdays/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["name"] == "Isana"
        assert data[0]["name"] == "Isana"
        assert data[0]["surname"] == "Gratis"
        assert data[0]["email"] == "test@email.com"
        assert data[0]["mobile"] == "111111111"
        assert "id" in data[0]

def test_update_contact_status(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.patch(
            "/api/contacts/1",
            json = {"done" : "True"}
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["done"] == "True"
        assert "id" in data[0]

def test_not_updated_contact_status(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.patch(
            "/api/contacts/1",
            json = {"done" : "True"}
        )

        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND

def test_remove_contact(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["name"] == "Isana"
        assert "id" in data


def test_repeat_delete_contact(client, token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND
