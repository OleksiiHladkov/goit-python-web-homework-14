from typing import List

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from contacts_book.database.db import get_db
from contacts_book.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from contacts_book.repository import users as repository_users
from contacts_book.services.auth import auth_service
from contacts_book.services.email import send_email
from contacts_book.conf import messages

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    The signup function creates a new user in the database.
    
    :param body: UserModel: Validate the request body against the usermodel schema
    :param background_tasks: BackgroundTasks: Add a task to the background tasks
    :param request: Request: Get the base url of the server
    :param db: Session: Get the database session
    :param : Get the user's email address
    :return: A dictionary with two keys: user and detail
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)

    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_ALREADY_EXISTS
        )

    body.password = auth_service.get_password_hash(body.password)

    new_user = await repository_users.create_user(body, db)

    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )

    return {"user": new_user, "detail": messages.USER_SUCCESSFULLY__CREATED}


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    The login function is used to authenticate a user.
    It takes in the username and password of the user, and returns an access token if successful.
    
    
    :param body: OAuth2PasswordRequestForm: Validate the request body
    :param db: Session: Get a database session from the sessionlocal class
    :return: A dict with access_token and refresh_token
    """
    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.EMAIL_NOT_CONFIRMED
        )

    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )

    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})

    await repository_users.update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token,
        a new refresh_token, and the type of token (bearer).
    
    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param db: Session: Get the database session
    :param : Get the credentials from the request header
    :return: A dictionary with the following keys:
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_REFRESH_TOKEN
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})

    await repository_users.update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it gets that user from the database and checks if they are already confirmed.
        If they are not, then their email is confirmed in our database.
    
    :param token: str: Get the token from the url
    :param db: Session: Get the database session
    :return: A dictionary with the message key
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=messages.VERIFICATION_ERROR
        )

    if user.confirmed:
        return {"message": messages.YOUR_EMAIL_IS_ALREADY_CONFIRM}

    await repository_users.confirmed_email(email, db)

    return {"message": messages.EMAIL_CONFIRMED}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    The request_email function is used to send an email to the user with a link
    to confirm their account. The function takes in the body of the request, which
    is a RequestEmail object containing an email address. It then checks if there is 
    a user associated with that email address and if so, sends them an email using 
    the send_email function from utils/mailer.py.
    
    :param body: RequestEmail: Pass the email address to the function
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the server
    :param db: Session: Get the database session
    :param : Get the user's email address
    :return: A string, but the return type is a dict
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user:
        if user.confirmed:
            return {"message": messages.YOUR_EMAIL_IS_ALREADY_CONFIRM}
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": messages.CHECK_YOUR_EMAIL}
