from typing import List , Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request

from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.connect import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail

from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email


router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
        body: UserModel,
        background_tasks: BackgroundTasks,
        request: Request,
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Provides signup functionality for a new user to the application.

    This function checks the validity of a user's email and password and returns a new user and sends an email notification
    that it was successfully created.

    :param body: The request body containing the user's email, password, and username.
    :type body: UserModel

    :param background_tasks: The background task of sending an email notification to the user with the base URL of the request.
    :type background_tasks: BackgroundTasks

    :param request: The request object.
    :type request: Request

    :param db: The database session.
    :type db: Session

    :return: Returns a dictionary containing the new user and a message that it was created.
    :rtype: Dict[str, Any]

    :raises HTTPException 409: If the user's email, password, or username already exists, a conflict error will be raised.

    """

    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Provides login functionality to the application.

    This function checks the validity of a user's email and password and returns access and refresh tokens if the login
    is successful.

    :param body: The request body containing the user's email and password.
    :type body: OAuth2PasswordRequestForm

    :param db: The database session.
    :type db: Session = Depends(get_db).

    :return: Returns a dictionary containing the access token, refresh token, and token type.
    :rtype: Dict[str, Any]

    :raises HTTPException 401: If the user's email or password is invalid or if the user's email is not confirmed.

    """

    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")

    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")

    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Provides the functionality of receiving a refreshed token.

        This function first decodes the token and then retrieves the user from the database.Then it creates new access and
        refresh token. If the refresh token is invalid, it raises HTTPException that it is invalid.

    :param credentials: Checks credentials of user
    :type credentials: HTTPAuthorizationCredentials = Security(security).

    :param db: The database session.
    :type db: Session = Depends(get_db).

    :return: Returns a dictionary containing the access token, refresh token, and token type.
    :rtype: dict

    :raises HTTPException 401: If the refreshed token is invalid, it gives an error of invalidity.

    """

    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> dict[str , str] | dict[str , str]:
    """
    Provides the functionality of confirming the email address.

        This function retrieves an email from the token and then retrieves the corresponding user from the database.
        If the user is not confirmed, it returns a message indicating that the email is not confirmed.
        If the user is confirmed, it updates the user's status to confirmed and returns a message indicating
        that the email has been confirmed.

    :param token: The token used to authorize the email and user.
    :type token: HTTPAuthorizationCredentials

    :param db: The database session.
    :type db: Session = Depends(get_db).

    :return: Returns a dictionary containing the message, that the email was confirmed or was already confirmed.
    :rtype: dict

    :raises HTTPException 400: If the user is not found in the database or if the email is already confirmed.

    """

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Email already confirmed"}

    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Provides the functionality of additional validation of the email address.
        This function retrieves a user from the database with its email address.
        If the user is valid, it returns a message indicating that the email is confirmed.
        If the user is confirmed, but the second validation is required then it sends a request for with background
        tasks to send an email with url to the user.

    :param body: The request body containing the email
    :type body: RequestEmail

    :param background_tasks: The background task of sending an email notification to the user with the base URL of the additional validation.
    :type background_tasks: BackgroundTasks

    :param request: Get the base_url of the application.
    :type request: Request

    :param db: The database session.
    :type db: Session=Depends(get_db).

    :return: Returns a dictionary containing the message, that the email was sent or to check email for confirmation.
    :rtype: dict

    """

    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}
