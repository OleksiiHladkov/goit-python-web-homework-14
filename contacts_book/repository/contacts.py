from typing import List
from datetime import datetime, timedelta

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from contacts_book.database.models import Contact, User
from contacts_book.schemas import ContactModel


async def get_contacts(
    limit: int, offset: int, search: str | None, user: User, db: Session
) -> List[Contact]:
    """
    The get_contacts function returns a list of contacts for the user.

    The get_contacts function takes in three parameters: limit, offset, and search.
    Limit is an integer that specifies how many contacts to return at once. Offset is an integer that specifies where to start returning contacts from (for pagination). Search is a string that filters the results by firstname, lastname or email address.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip before returning
    :param search: str | None: Filter the contacts by firstname, lastname or email
    :param user: User: Get the user id to filter the contacts by
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    """
    if search:
        return (
            db.query(Contact)
            .filter(
                and_(
                    Contact.user_id == user.id,
                    or_(
                        Contact.firstname.icontains(search),
                        Contact.lastname.icontains(search),
                        Contact.email.icontains(search),
                    ),
                )
            )
            .limit(limit)
            .offset(offset)
            .all()
        )

    return (
        db.query(Contact)
        .filter(Contact.user_id == user.id)
        .limit(limit)
        .offset(offset)
        .all()
    )


async def get_contact_by_id(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    The get_contact_by_id function returns a contact from the database based on its id.


    :param contact_id: int: Specify the id of the contact you want to get
    :param user: User: Get the user_id from the user object
    :param db: Session: Pass a database session to the function
    :return: A contact object or none
    """
    return (
        db.query(Contact)
        .filter(Contact.user_id == user.id, Contact.id == contact_id)
        .first()
    )


async def get_contact_by_unique_fields(
    body: ContactModel, user: User, db: Session
) -> Contact | None:
    """
    The get_contact_by_unique_fields function is used to retrieve a contact from the database by either phone or email.
        The function takes in a ContactModel object, which contains the phone and/or email of the contact we are looking for.
        It also takes in an authenticated user object, so that we can ensure that only contacts belonging to this user are returned.

    :param body: ContactModel: Get the contact model from the request body
    :param user: User: Get the user id from the user object
    :param db: Session: Pass the database session to the function
    :return: An object of the contact class or none
    """
    return (
        db.query(Contact)
        .filter(
            and_(
                Contact.user_id == user.id,
                or_(Contact.phone == body.phone, Contact.email == body.email),
            )
        )
        .first()
    )


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    The create_contact function creates a new contact in the database.

    The create_contact function takes a ContactModel object and uses it to create a new contact in the database. The user is also passed into this function, as well as an SQLAlchemy Session object for interacting with the database. This function returns an instance of Contact that was created.

    :param body: ContactModel: Pass the contact model to the function
    :param user: User: Get the user id from the jwt token
    :param db: Session: Pass the database session into the function
    :return: An instance of contact
    """
    contact = Contact(user=user, **body.model_dump())

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact


async def update_contact(
    body: ContactModel, contact_id: int, user: User, db: Session
) -> Contact | None:
    """
    The update_contact function updates a contact in the database.
        Args:
            body (ContactModel): The updated contact information.
            contact_id (int): The id of the contact to update.
            user (User): The current logged-in user, used for authorization purposes.
            db (Session): A database session object that is used to query and commit changes to the database.

    :param body: ContactModel: Get the data from the request body
    :param contact_id: int: Identify which contact to update
    :param user: User: Check if the user is authorized to update the contact
    :param db: Session: Pass the database session to the function
    :return: A contact object
    """
    contact = await get_contact_by_id(contact_id, user, db)

    if contact:
        contact.firstname = body.firstname
        contact.lastname = body.lastname
        contact.phone = body.phone
        contact.email = body.email
        contact.birthday = body.birthday
        contact.description = body.description

        db.commit()

    return contact


async def delete_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            user (User): The user who is deleting the contact.
            db (Session): A database session object for interacting with the database.
        Returns:
            Contact: The deleted Contact object, or None if no such Contact exists.

    :param contact_id: int: Specify the contact that is to be deleted
    :param user: User: Get the user's id from the database
    :param db: Session: Pass the database session to the function
    :return: The contact that was deleted
    """
    contact = await get_contact_by_id(contact_id, user, db)

    if contact:
        db.delete(contact)
        db.commit()

    return contact


async def get_upcoming_birthdays(user: User, db: Session) -> List[Contact]:
    """
    The get_upcoming_birthdays function returns a list of contacts whose birthdays are within the next seven days.
        Args:
            user (User): The user who is requesting the upcoming birthdays.
            db (Session): A database session to use for querying data from the database.
        Returns:
            List[Contact]: A list of contacts whose birthdays are within the next seven days.

    :param user: User: Get the user's id from the database
    :param db: Session: Pass the database session to the function
    :return: A list of contacts with upcoming birthdays
    """
    res_contacts = []
    cur_contacts = []

    # get contacts with limit and offset -- for future optimization
    # limit = 100
    # offset = 0
    # flag = True
    # while flag:
    #     contacts_db = await get_contacts(limit, offset, None, user, db)
    #     if not len(contacts_db):
    #         flag = False
    #     cur_contacts.extend(contacts_db)
    #     offset += limit
    cur_contacts = await get_contacts(100000, 0, None, user, db)

    # get list of next seven days
    date = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
    list_dates = []

    count = 1
    while count <= 7:
        date += timedelta(1)
        # year = 1 for next equalization dates by month and day
        list_dates.append(datetime(1, date.month, date.day))
        count += 1

    # equalization dates
    for contact in cur_contacts:
        # year = 1, this is equalization dates by month and day
        if datetime(1, contact.birthday.month, contact.birthday.day) in list_dates:
            res_contacts.append(contact)

    return res_contacts
