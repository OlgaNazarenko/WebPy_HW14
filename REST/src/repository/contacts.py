from datetime import datetime, timedelta
from typing import List, Sequence

from sqlalchemy import func, Row, select
from sqlalchemy.sql import text

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.database.model import Contact, User
from src.schemas import ContactModel, ContactStatusUpdate
from src.repository.users import get_user_by_email


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    Creates a new contact.

    :param body: The data for the contact to create.
    :type body: ContactModel

    :param user: The user to create contact for.
    :type user: User

    :param db: The database session.
    :type db: Session

    :return: The newly created contact.
    :rtype: Contact

    """

    contact = Contact(
        name=body.name,
        surname=body.surname,
        email=body.email,
        mobile=body.mobile,
        date_of_birth=body.date_of_birth,
        user_id=user.id
    )
    db.add(contact)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError("Failed to create user", str(e))
    db.refresh(contact)

    return contact


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Retrieves a list of contacts with specified pagination parameters.

    :param skip: The number of contacts to skip.
    :type skip: int

    :param limit: The maximum number of contacts to return.
    :type limit: int

    :param user: The user to retrieve contacts for.
    :type user: User

    :param db: The database session.
    :type db: Session

    :return: A list of notes.
    :rtype: List[Contact]

    """

    contact = db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()
    return contact


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Retrieves a contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve
    :type contact_id: int

    :param user: The user to retrieve the contact for.
    :type user: User

    :param db: The database session.
    :type db: Session

    :return: The contact with the specified ID
    :rtype: Contact__all__ = [
    "create_contact",
    "get_contact",
    "get_contacts",
    "update_contact",
    "get_contacts_choice",
    "get_contacts_birthdays",
    "update_contact_status",
    "remove_contact",
    "update_avatar"
]

    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def update_contact(body: ContactModel, contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Updates a single contact with the specified ID for a specific user.

    :param body: The updated data for the contact.
    :type body: ContactModel

    :param contact_id: the specific the contact id that is updated
    :type contact_id: int

    :param user: The user to update contact for.
    :type user: User

    :param db: The database session.
    :type db: Session

    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None

    """

    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.mobile = body.mobile
        contact.date_of_birth = body.date_of_birth
        db.commit()
    return contact


async def get_contacts_choice(name: str | None, surname: str | None,
                              email: str | None, user: User, db: Session) -> list[Contact]:
    """
    Allows to search for a contact based either on name, surname, or email.

    :param name: The name of the contact to search for.
    :type name: str | None

    :param surname: The surname of the contact to search for.
    :type surname: str | None

    :param email: The email of the contact to search for.
    :type email: str | None

    :param user: The user to get the contact.
    :type user: User

    :param db: The database session.
    :type db: Session

    :return: The list of contacts.
    :rtype: list[Contact]

    """

    contacts = db.query(Contact).filter(and_(or_(
        Contact.name.like(f"%{name}%"), Contact.surname.like(f"%{surname}%"), Contact.email.like(f"%{email}%")),
        Contact.user_id == user.id)
    ).all()

    return contacts


async def get_contacts_birthdays(user: User, db: Session) -> List[Contact]:
    """
    Allows to search for a list of contacts, who have birthdays in 7 days from today.

    :param user: The user to get the contact.
    :type user: User

    :param db: The database session.
    :type db: Session

    :return: The list of contacts.
    :rtype: list[Contact]

    """

    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=7)

    params = {"start_date" : start_date.strftime("%m-%d"), "end_date": end_date.strftime("%m-%d")}

    contacts = db.execute(
        text("SELECT * FROM contacts WHERE TO_CHAR(date_of_birth, 'MM-DD') BETWEEN :start_date AND :end_date "
             "AND TO_CHAR(date_of_birth, 'MM-DD') <> :start_date"),
        params
    ).fetchall()

    return contacts


async def update_contact_status(body: ContactStatusUpdate, contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Updates a single contact with the specified ID for a specific user.

    :param body: The updated data for the contact.
    :type body: ContactStatusUpdate

    :param contact_id: The ID of the contact to update.
    :type contact_id: int

    :param user: The user to get the contact.
    :type user: User

    :param db: The database session.
    :type db: Session

    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None

    """

    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

    if contact:
        contact.done = body.done
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Removes a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int

    :param user: The user to remove the contact.
    :type user: User

    :param db: The database session.
    :type db: Session

    :return: The removed contact, or None if it does not exist.
    :rtype: Contact | None

    """

    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Updates the avatar of a user with the specified email address.

    :param email: The email address of the user whose avatar is being updated.
    :type email: str

    :param url: The URL of the new avatar image.
    :type url: str

    :param db: The database session.
    :type db: Session

    :return: The user whose avatar was updated.
    :rtype: User

    """

    updated_user = await get_user_by_email(email, db)
    updated_user.avatar = url
    db.commit()
    return updated_user
