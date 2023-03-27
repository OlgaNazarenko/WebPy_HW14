from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import TextClause

from src.database.model import User
from src.services.auth import auth_service
from src.conf.messages import (
    NOT_FOUND, CREATE_CONTACT_FAILED, NOT_FOUND_CONTACT
)


@pytest.fixture()
def access_token(client, user, session, monkeypatch):
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


@pytest.fixture(scope="module")
def contact():
    return {
                "name": "Isana",
                "surname": "Gratis",
                "email": "test@example.com",
                "mobile": "111111111",
                "date_of_birth": "2000-03-21",
                "done": False
            }


class TestCreateContact:
    def test_create_contact(self, client, access_token, contact):
        with patch.object(auth_service, 'redis') as r_mock:
            r_mock.get.return_value = None

            response = client.post(
                "/api/contacts/new/",
                json=contact,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 201, response.text
            data = response.json()

            assert data["name"] == contact["name"]
            assert data["surname"] == contact["surname"]
            assert data["email"] == contact["email"]
            assert data["mobile"] == contact["mobile"]
            assert data["date_of_birth"] == contact["date_of_birth"]
            assert "id" in data

    def test_create_contact_not_found(self, client, access_token, contact):
        with patch.object(auth_service, 'redis') as r_mock:
            r_mock.get.return_value = None

            response = client.post(
                "/api/contacts/new/",
                json = contact,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 400, response.text
            assert response.json()["detail"] == CREATE_CONTACT_FAILED


class TestGetContacts:
    def test_get_contacts(self, client, access_token, mocker):
        with patch.object(auth_service, 'redis') as r_mock:
            mocker.patch('src.routes.contacts.RateLimiter.__call__', autospec=True)
            r_mock.get.return_value = None

            response = client.get(
                "/api/contacts",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200, response.text
            data = response.json()
            assert isinstance(data, list)
            assert data[0]["name"] == "Isana"
            assert "id" in data[0]


class TestGetContact:
    def test_get_contact(self, client, access_token):
        with patch.object(auth_service, 'redis') as r_mock:
            r_mock.get.return_value = None

            response = client.get(
                "/api/contacts/1",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200, response.text
            data = response.json()
            assert data["name"] == "Isana"
            assert "id" in data

    def test_get_contact_not_found(self, client, access_token, mocker):
        with patch.object(auth_service, 'redis') as r_mock:
            mocker.patch('src.routes.contacts.RateLimiter.__call__', autospec = True)
            r_mock.get.return_value = None

            response = client.get(
                "/api/contact/2",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 404, response.text
            data = response.json()
            assert data["detail"] == NOT_FOUND_CONTACT


class TestUpdateContact:
    def test_update_contact(self, client, access_token, contact):
        with patch.object(auth_service, 'redis') as r_mock:
            r_mock.get.return_value = None

            contact.update(
                {
                    "name": "Composition",
                    "surname": "Norcom",
                    "email": "test2@email.com",
                    "mobile": "222222222",
                    "date_of_birth": "2000-03-28"
                }
            )

            response = client.put(
                "/api/contacts/1",
                json=contact,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200, response.text
            data = response.json()
            assert data["name"] == contact["name"]
            assert data["surname"] == contact["surname"]
            assert data["email"] == contact["email"]
            assert data["mobile"] == contact["mobile"]
            assert data["date_of_birth"] == contact["date_of_birth"]
            assert "id" in data

    def test_update_contact_not_found(self, client, access_token, contact):
        with patch.object(auth_service, 'redis') as r_mock:
            r_mock.get.return_value = None

            response = client.put(
                "/api/contacts/2",
                json=contact,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 404, response.text
            assert response.json()["detail"] == NOT_FOUND_CONTACT


class TestGetContactsByQuery:
    @pytest.mark.parametrize(
        "name, surname, email",
        [
            ("Composition", None, None),
            (None, "Norcom", None),
            (None, None, "test2@email.com", )
        ]
    )
    def test_get_contacts_by_query(self, client, access_token, name, surname, email, contact):
        with patch.object(auth_service, "redis") as r_mock:
            r_mock.get.return_value = None

            if name:
                params = {"name": name}
            elif surname:
                params = {"surname": surname}
            elif email:
                params = {"email": email}

            response = client.get(
                "/api/contacts/by_choice/",
                params=params,
                headers = {"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200, response.text
            data = response.json()
            assert isinstance(data, list)
            assert data[0]["email"] == contact["email"]
            assert "id" in data[0]


class TestGetContactsBirthdays:
    def test_get_contacts_birthdays(self, client, access_token, mocker, contact):
        with patch.object(auth_service, 'redis') as r_mock:
            r_mock.get.return_value = None

            mocker.patch(
                "src.repository.contacts.text",
                return_value = TextClause(
                    "SELECT * FROM contacts WHERE strftime('%m-%d', date_of_birth) BETWEEN :start_date AND :end_date"
                ),
            )

            response = client.get(
                "/api/contacts/birthdays/",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200, response.text
            print(response.text)
            data = response.json()
            assert isinstance(data, list)

            assert data[0].get("email") == contact["email"]
            assert "id" in data[0]


class TestUpdateContactStatus:
    def test_update_contact_status(self, client, access_token, contact):
        with patch.object(auth_service, 'redis') as r_mock:
            r_mock.get.return_value = None

            response = client.patch(
                "/api/contacts/1",
                json = {"done": True},
                headers = {"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200, response.text
            data = response.json()
            assert data["done"] == True
            assert "id" in data

#
# # def test_not_updated_contact_status(client, token):
# #     with patch.object(auth_service, 'redis') as r_mock:
# #         r_mock.get.return_value = None
# #         response = client.patch(
# #             "/api/contacts/1",
# #             json = {"done" : "True"}
# #         )
# #
# #         assert response.status_code == 404, response.text
# #         data = response.json()
# #         print(data)
# #         assert data["detail"] == NOT_FOUND
#


class TestRemoveContact:
    def test_remove_contact(self, client, access_token, contact):
        with patch.object(auth_service, 'redis') as r_mock:
            r_mock.get.return_value = None

            response = client.delete(
                "/api/contacts/1",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200, response.text
            assert response.json()["name"] == contact["name"]
            assert response.json()["email"] == contact["email"]
            assert "id" in response.json()

    def test_repeat_delete_contact(self, client, access_token):
        with patch.object(auth_service, 'redis') as r_mock:
            r_mock.get.return_value = None

            response = client.delete(
                "/api/contacts/1",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 404, response.text
            assert response.json()["detail"] == "Not Found"
