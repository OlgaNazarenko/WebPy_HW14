"""
Auth module
____________
This is Module, which has authentication (the class was created).

"""

from datetime import datetime, timedelta
from typing import Optional
import pickle
import redis as redis_db

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database.connect import get_db
from src.repository import users as repository_users
from src.conf.config import settings
from src.conf.messages import UNAUTHORIZED


class Auth:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SECRET_KEY = settings.secret_key_jwt
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    redis = redis_db.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the pwd_context object to verify that the
        plain-text password matches the hashed one.

        :param self: Represent the instance of the class

        :param plain_password: Pass in the password that is entered by the user

        :param hashed_password: Compare the password that is being entered to the hashed password in the database

        :return: A boolean value

        """

        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

        :param self: Represent the instance of the class

        :param password: Get the password from the user
        :type password: str

        :return: A password hash

        """

        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): A dictionary containing the claims to be encoded in the JWT.
                expires_delta (Optional[float]): An optional timedelta of seconds for the expiration time of this token.

        :param self: Represent the instance of the class

        :param data: Pass in the data to be encoded into the jwt
        :type data: dict

        :param expires_delta: Set the expiration time of the token
        :type expires_delta: Optional[float] = None

        :return: An encoded access token
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the refresh token expires. Defaults to
                None, which sets it to 7 days from now.

        :param self: Represent the instance of the class

        :param data: Store the data that we want to encode into our token
        :type data: dict

        :param expires_delta: Set the expiration time of the refresh token
        :type expires_delta: Optional[float]

        :return: A refresh token
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds = expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days = 7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope" : "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm = self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.
        It takes in a refresh_token as an argument and returns the email of the user if successful.
        If it fails, it raises an HTTPException with status code 401 (UNAUTHORIZED) and detail message &quot;Could
        not validate credentials&quot;.

        :param self: Represent the instance of the class

        :param refresh_token: Pass in the refresh token that is sent from the client
        :type refresh_token: str

        :return: The email of the user who owns the refresh token

        """

        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED)

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the
            UserRouter class. It takes an OAuth2 token as input and returns the user
            associated with that token. If no user is found, it raises an exception.

        :param self: Represent the instance of the class

        :param token: Get the token from the authorization header
        :type token: str

        :param db: Get the database connection from the dependency injection.
        :type db: Session

        :return: The user object that is associated with the token

        """

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email: str = payload['sub']
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = self.redis.get(f"users:{email}")
        if user is None:
            print('GET USER FROM POSTGRES')
            user = await repository_users.get_user_by_email(email, db)
            if user is None :
                raise credentials_exception
            self.redis.set(f"users:{email}", pickle.dumps(user))
            self.redis.expire(f"users:{email}", 900)
        else:
            print('GET USER FROM CACHE')
            user = pickle.loads(user)
        return user

    async def create_email_token(self, data: dict):
        """
        The create_email_token function takes in a dictionary of data and returns a token.
        The token is created using the JWT library, which encodes the data into a string that can be decoded later.
        The function adds an expiration date to the encoded data, as well as some other information about how it was encoded.

        :param self: Represent the instance of the class

        :param data: Pass the data to be encoded into the token.
        :type data: dict

        :return: A token that is used to verify the user's email address

        """

        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email associated with that token.
            If the scope of the token is not 'email_token', then it raises an HTTPException with status code 401 (Unauthorized).
            If there is a JWTError, then it raises an HTTPException with status code 422 (Unprocessable Entity).

        :param self: Represent the instance of the class

        :param token: Pass the token value to the function
        :type token: str

        :return: The email address of the user

        """

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'email_token':
                email = payload["sub"]
                return email
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED , detail = 'Invalid scope for token')
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
