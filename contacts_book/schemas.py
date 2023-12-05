from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


# Contacts
class ContactBase(BaseModel):
    firstname: str = Field(min_length=1, max_length=50)


class ContactModel(ContactBase):
    lastname: str = Field(max_length=50)
    email: EmailStr
    phone: str
    birthday: datetime
    description: str


class ContactResponce(ContactModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Users
class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
