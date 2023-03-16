import sys
import os

from sqlalchemy import or_

# add parent directory of src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.schemas import ContactModel, ContactUpdate, ContactStatusUpdate
from src.database.model import Contact, User
from src.repository.contacts import (
    create_contact,
    get_contacts,
    get_contact,
    update_contact,
    get_contacts_choice,
    get_contacts_birthdays,
    update_contact_status,
    remove_contact,
    update_avatar
)
from src.repository.users import get_user_by_email


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        # returns a contact based on its ID

        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        # checks the above function, test_get_contact_found, if it is correct and if it is not found based on a given ID

        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(
            name="test",
            surname="TestContact",
            email="test@test.com",
            mobile="0932323321",
            date_of_birth="1999-01-25"
        )

        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.mobile, body.mobile)
        self.assertEqual(result.date_of_birth, body.date_of_birth)
        self.assertEqual(result.user_id , self.user.id)
        self.assertTrue(hasattr(result , "id"))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        # checks the above function, if it works correctly or not. If that contact is None.

        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactModel(
            name="test",
            surname="TestContact",
            email = "test@test.com",
            mobile = "0932323321",
            date_of_birth = "1994-01-25"
        )

        contact = Contact(
            name = "test2",
            surname = "TestContact2",
            email = "test2@test.com",
            mobile = "0932222222",
            date_of_birth = "1994-03-10"
        )

        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(body=body, contact_id=1, user=self.user, db=self.session)

        self.assertEqual(result, contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.mobile, body.mobile)
        self.assertEqual(result.date_of_birth, body.date_of_birth)
        self.assertTrue(hasattr(result, "id"))


    async def test_update_contact_not_found(self):
        body = ContactModel(
            name = "test3" ,
            surname = "TestContact3" ,
            email = "test3@test.com" ,
            mobile = "093333333" ,
            date_of_birth = "1993-03-13"
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(body=body, contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_status_contact_found(self):
        body = ContactStatusUpdate(done=True)
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact_status(body=body,contact_id=1,user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_status_contact_not_found(self):
        # check the validity of the above function, if the contact is not found.

        body = ContactStatusUpdate(done=True)
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact_status(body=body,contact_id=1,user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contacts_birthdays(self) :
        today = datetime.now().date()
        contacts = [
            Contact(date_of_birth=(today + timedelta(days=7))),
            Contact(date_of_birth=(today + timedelta(days=7))),
            Contact(date_of_birth=(today + timedelta(days=7))),
        ]

        self.session.execute.return_value.fetchall.return_value = contacts
        result = await get_contacts_birthdays(user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_update_avatar(self):
        user = User(email='test@instance.com', avatar='https://instance.com/avatar.jpg')
        self.session.add(user)
        self.session.commit()

        new_avatar_url='https://instance.com/new_avatar.jpg'
        await update_avatar(email='test@example.com', url=new_avatar_url, db=self.session)

        updated_user = await get_user_by_email(email='test@example.com', db=self.session)

        self.assertEqual(updated_user.avatar, new_avatar_url)

async def test_contacts_choice(self):
    contact1 = Contact(name="Tommy", surname="Huyng", email="tommy.huyng@test.com", user=self.user)
    contact2 = Contact(name="Jin", surname="Cha", email="jin.cha@test.com", user=self.user)
    contact3 = Contact(name="Lee", surname="Ji", email="li.ji@test.com", user=self.user)

    self.session.add_all([contact1, contact2, contact3])
    self.session.commit()

    result = await get_contacts_choice(name="", surname="Huyng", email="", user=self.user, db=self.session)
    self.assertEqual(result.name, contact1.name)
    self.assertEqual(result.surname,contact1.surname)
    self.assertEqual(result.email, contact1.email)

    result = await get_contacts_choice(name="Jin", surname="", email="", user=self.user, db=self.session)
    self.assertEqual(result.name, contact2.name)
    self.assertEqual(result.surname, contact2.surname)
    self.assertEqual(result.email, contact2.email)

    result = await get_contacts_choice(name="", surname="", email="li.ji@test.com", user=self.user, db=self.session)
    self.assertEqual(result.name, contact3.name)
    self.assertEqual(result.surname, contact3.surname)
    self.assertEqual(result.email, contact3.email)


if __name__ == '__main__':
    unittest.main()
