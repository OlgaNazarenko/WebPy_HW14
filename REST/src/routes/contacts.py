from typing import List

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, HTTPException, status, Path, Form, Query, Response, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import EmailStr
from fastapi_limiter.depends import RateLimiter

from src.schemas import (ContactModel, ContactUpdate, ContactResponse, ContactStatusUpdate, ContactResponseChoice,
                         UserDb)
from src.repository import contacts as repository_contacts
from src.database.connect import get_db
from src.database.model import User, Contact
from src.conf.config import settings
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.post("/new/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactModel object as input, which is validated by pydantic.
        If the validation fails, an HTTPException with status code 400 is raised and returned to the user.

    :param body: Get the contact information from the request.
    :type body: ContactModel

    :param db: Get the database session.
    :type db: Session = Depends(get_db).

    :param current_user: Get the current user from the database.
    :type current_user: User=Depends(auth_service.get_current_user).

    :return: A contact object.
    :rtype: Contact

    """
    contact = await repository_contacts.create_contact(body, current_user, db)

    if contact is None:
        raise HTTPException(status_code = 400, detail = "Creation of contact failed")

    return contact


@router.get('/', response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)) -> list[Contact]:
    """
    The get_contacts function returns a list of contacts.
        The skip and limit parameters are used to paginate the results.

    :param skip: Skip the first n contacts.
    :type skip: int

    :param limit: Limit the number of contacts returned.
    :type limit: int

    :param db: Inject the database session into the function.
    :type db: Session=Depends(get_db)

    :param current_user: Get the current user.
    :type current_user: User=Depends(auth_service.get_current_user).

    :return: A list of contacts
    :rtype: list

    """

    contacts = await repository_contacts.get_contacts(skip, limit,current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    The get_contact function returns a contact by its id.
        The function takes the following parameters:
            - contact_id: int, the id of the contact to be returned.
            - db: Session = Depends(get_db), an instance of a database session object that is used for querying and updating data in our database. This parameter is automatically injected into this function by FastAPI when it calls this function because we have added it as a dependency using @Depends(). We also use @Depends() to inject an instance of our current user into this function so that we can check if they are authorized to access this

    :param contact_id: Specify the id of the contact to be fetched.
    :type contact_id: int

    :param db: Get the database session.
    :type db: Session=Depends(get_db)

    :param current_user: Get the current user.
    :type current_user: User=Depends(auth_service.get_current_user).

    :return: A contact object
    :rtype: Contact

    """

    contact = await repository_contacts.get_contact(contact_id, current_user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    The update_contact function updates a contact in the database.

    The function takes in a ContactUpdate object, which is defined by the Pydantic library.
    This object contains all the fields that can be updated for a contact, and it validates them as well.

    :param body: Pass the contact information to be updated.
    :type body: ContactUpdate

    :param contact_id: Specify the contact ID to update.
    :type contact_id: int

    :param db: Get the database session.
    :type db: Session=Depends(get_db)

    :param current_user: Get the current user.
    :type current_user: User=Depends(auth_service.get_current_user)

    :return: A contact object.
    :rtype: Contact

    """

    contact = await repository_contacts.update_contact(body, contact_id, current_user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    return contact


@router.get("/by_choice/", response_model=ContactResponseChoice)
async def get_contacts_choice(name: str | None = None,
                              surname: str | None = None,
                              email: EmailStr | None = None,
                              db: Session = Depends(get_db),
                              current_user: User = Depends(auth_service.get_current_user)) -> Contact | list[Contact]:
    """
    The get_contacts_choice function is used to get a contact or the list of contacts either by name or by surname or by email.

    The function takes in the following parameters:
        - name (str): The first name of the contact.
        - surname (str): The last name of the contact.
        - email (EmailStr): An email address for a user's account.

    :param name: Get the name of a contact.
    :type name: str | None

    :param surname: Filter the contacts by surname.
    :type surname: str | None

    :param email: Validate the email address.
    :type email: EmailStr | None

    :param db: Get a database session, which is required for accessing the contacts.
    :type db: Session=Depends(get_db)

    :param current_user: Get the user that is currently logged in.
    :type current_user: User=Depends(auth_service.get_current_user)

    :return: A list of contacts or a contact that meet the criteria.
    :rtype: Contact | list[Contact]

    """

    contact = await repository_contacts.get_contacts_choice(name, surname, email, current_user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    print(f"name: {name}, surname: {surname}, email: {email}")
    return contact


@router.get('/birthdays/', response_model=List[ContactResponse])
async def get_contacts_birthdays(db: Session = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)) -> list[Contact]:
    """
    The get_contacts_birthdays function returns a list of contacts that have birthdays in the current month.

    The function takes two parameters: db and current_user.
    The db parameter is used to access the database, while the current_user parameter is used to get information about
    who made this request.

    :param db: Get the database session.
    :type db: Session=Depends(get_db)

    :param current_user: Get the current user.
    :type current_user: User=Depends(auth_service.get_current_user)

    :return: A list of contacts, who have birthdays in 7 days
    :rtype: list[Contact]

    """

    contacts = await repository_contacts.get_contacts_birthdays(current_user, db)

    return contacts


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact_status(body: ContactStatusUpdate,
                                contact_id: int,
                                db: Session = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    The update_contact_status function updates the status of a contact.

    The function takes in a ContactStatusUpdate object, which contains the new status for the contact.
    It also takes in an integer representing the id of the contact to be updated and two dependencies: db and current_user.
    The db dependency is used to access our database, while current_user is used to get information about who made this request.

    :param body: Get the contact status from the request body.
    :type body: ContactStatusUpdate

    :param contact_id: Identify the contact to be updated.
    :type contact_id: int

    :param db: Get a database session.
    :type db: Session=Depends(get_db)

    :param current_user: Get the current user.
    :type current_user: User=Depends(auth_service.get_current_user)

    :return: The updated contact.
    :rtype: Contact

    """

    contact = await repository_contacts.update_contact_status(body, contact_id,current_user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_contact function removes a contact from the database.

    :param contact_id: Specify the contact to be removed.
    :type contact_id: int

    :param db: Pass the database session to the function.
    :type db: Session=Depends(get_db)

    :param current_user: Get the current user.
    :type current_user: User=Depends(auth_service.get_current_user)

    :return: A contact, but it is not used in the frontend.
    :rtype: None

    """

    contact = await repository_contacts.remove_contact(contact_id, current_user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    return contact
