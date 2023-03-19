from sqlalchemy.orm import Session

from src.database.model import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists,
    it will return None.

    :param email: Specify the type of parameter that will be passed into the function.
    :type email: str

    :param db: Pass the database session to the function
    :type db: Session

    :return: The first user with the specified email address

    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user.

    :param body: The data for the user to create.
    :type body: UserModel

    :param db: The database session.
    :type db: Session

    :return: The newly created user.
    :rtype: User

    """

    new_user = User(**body.dict())
    db.add(new_user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError("Failed to create user", str(e))
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> User:
    """
    Updates the token used for user login.

    :param user: The user for which the token is being updated.
    :type user: User

    :param token: The new token to use for login, or None to invalidate the token.
    :type token: str | None

    :param db: The database session.
    :type db: User or Session

    :return: The updated user.
    :rtype: User

    """

    user.refresh_token = token
    db.commit()
    db.refresh(user)
    return user


async def confirmed_email(email: str, db: Session) -> User:
    """
    Marks the specified email address as confirmed for user login.
        When a user creates an account, they are typically sent a confirmation email to verify
        their email address. Once the user has clicked the confirmation link and their email
        address has been verified, this function should be called to mark the email as confirmed.

    :param email: The email address to mark as confirmed.
    :type email: str

    :param db: The database session.
    :type db: Session

    :return: The confirmed user.
    :rtype: User

    """

    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
    db.refresh(user)
    return user


async def update_avatar(email: str, url: str, db: Session) -> User:
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
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user
