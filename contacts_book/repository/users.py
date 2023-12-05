from sqlalchemy.orm import Session

from contacts_book.database.models import User
from contacts_book.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function returns a user object from the database based on the email address provided.
        Args:
            email (str): The email address of the user to be retrieved.
            db (Session): A connection to a database session.
        Returns:
            User: A single user object matching the provided email address.
    
    :param email: str: Pass in the email of the user to be retrieved
    :param db: Session: Connect to the database
    :return: A user object
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
        
    
    :param body: UserModel: Create a new user
    :param db: Session: Pass the database session to the function
    :return: A new user object
    """
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.
    
    :param user: User: Identify the user that is being updated
    :param token: str | None: Store the refresh token in the database
    :param db: Session: Make changes to the database
    :return: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function is used to confirm a user's email address.
        Args:
            email (str): The user's email address.
            db (Session): A database session object.
    
    :param email: str: Get the email of the user
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.
        Args:
            email (str): The email of the user to update.
            url (str): The new URL for the avatar image.
            db (Session, optional): SQLAlchemy Session instance. Defaults to None.
    
    :param email: Get the user from the database
    :param url: str: Specify the type of data that is expected to be passed into the function
    :param db: Session: Pass in the database session
    :return: The user object
    """
    user = await get_user_by_email(email, db)
    if user:
        user.avatar = url
        db.commit()
    return user