from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime


class ContactModel(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    surname: str = Field(min_length=3, max_length=50)
    email: EmailStr
    mobile: str = Field(min_length=9, max_length=25)
    date_of_birth: date

class ContactUpdate(ContactModel):
    done: bool

class ContactStatusUpdate(BaseModel):
    done: bool

class ContactResponse(ContactModel):
    id: int

    class Config:
        orm_mode = True

class ContactResponseChoice(ContactModel):
    name: str | None = None
    surname: str | None = None
    email: EmailStr | None = None
    mobile: str | None = None
    date_of_birth: date | None = None

    class Config:
        orm_mode = True

class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    email: EmailStr
    password: str = Field(min_length=5, max_length=25)

class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User has been created"

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    email: EmailStr
