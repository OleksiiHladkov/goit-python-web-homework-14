from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from contacts_book.database.db import get_db
from contacts_book.database.models import User
from contacts_book.schemas import ContactModel, ContactResponce
from contacts_book.repository import contacts as repository_contacts
from contacts_book.services.auth import auth_service
from contacts_book.conf import messages

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get(
    "/",
    response_model=List[ContactResponce],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    name="Read contacts",
)
async def get_contacts(
    limit: int = Query(10, le=100),
    offset: int = 0,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contacts function returns a list of contacts.
    
    :param limit: int: Limit the number of contacts returned
    :param le: Limit the number of contacts returned to 100
    :param offset: int: Specify the number of records to skip before returning results
    :param search: str | None: Search for contacts by name
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :param : Limit the number of contacts returned
    :return: A list of contacts
    """
    return await repository_contacts.get_contacts(
        limit, offset, search, current_user, db
    )


@router.get(
    "/upcoming_birthdays",
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    name="Upcoming birthdays",
)
async def get_upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contact function returns a list of contacts that have upcoming birthdays.
        The current_user is passed in as an argument to the function, and then used to query the database for all contacts associated with that user.
        The get_upcoming_birthdays function from repository/contacts.py is called, which queries the database for all contacts whose birthday falls within 7 days of today's date.
    
    :param db: Session: Get the database session
    :param current_user: User: Get the current user's id
    :param : Get the current user and the db parameter is used to get a database connection
    :return: A list of contacts
    """
    return await repository_contacts.get_upcoming_birthdays(current_user, db)


@router.get(
    "/{contact_id}",
    response_model=ContactResponce,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    name="Read contact",
)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contact function returns a contact by its id.
    
    :param contact_id: int: Get the contact id from the url
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :param : Get the contact id from the url
    :return: A contact object
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user, db)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found!"
        )

    return contact


@router.post(
    "/",
    response_model=ContactResponce,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=30))],
    name="Create contact",
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    body: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactModel: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :param : Get the database connection
    :return: A contactmodel object
    """
    contact = await repository_contacts.get_contact_by_unique_fields(
        body, current_user, db
    )

    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.CONTACT_ALREADY_AXISTS,
        )

    contact = await repository_contacts.create_contact(body, current_user, db)

    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponce,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=30))],
    name="Read contact",
)
async def update_contact(
    body: ContactModel,
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The update_contact function updates a contact in the database.
    
    :param body: ContactModel: Pass the contact data to the function
    :param contact_id: int: Get the contact id from the url
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :param : Get the contact id from the url path
    :return: A contactmodel object
    """
    contact = await repository_contacts.get_contact_by_unique_fields(
        body, current_user, db
    )

    if contact and contact.id != contact_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.CONTACT_ALREADY_AXISTS,
        )

    contact = await repository_contacts.update_contact(
        body, contact_id, current_user, db
    )

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )

    return contact


@router.delete(
    "/{contact_id}",
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=30))],
    name="Delete contact",
)
async def delete_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The delete_contact function deletes a contact from the database.
        The function takes in an integer representing the id of the contact to be deleted,
        and returns a dictionary containing information about that contact.
    
    :param contact_id: int: Get the contact id from the url
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :param : Get the id of the contact that is to be deleted
    :return: A contact object
    """
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )

    return contact
