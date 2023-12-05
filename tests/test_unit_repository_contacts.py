import asyncio
import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta


from sqlalchemy.orm import Session


from contacts_book.database.models import Contact, User
from contacts_book.schemas import ContactModel
from contacts_book.repository.contacts import (
    get_contacts,
    get_contact_by_id,
    get_contact_by_unique_fields,
    get_upcoming_birthdays,
    create_contact,
    update_contact,
    delete_contact,
)


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email="test@test.com")
        self.body = ContactModel(
            firstname="Leya",
            lastname="Organa",
            email="leyaorgana@meta.ua",
            phone="+380661111111",
            birthday=datetime(1989, 12, 6),
            description="love Han",
        )
        self.contact_id = 1

    async def test_get_cats(self):
        contacts = [Contact(), Contact(), Contact()]

        self.session.query().filter().limit().offset().all.return_value = contacts
        result = await get_contacts(10, 0, None, self.user, self.session)
        self.assertEqual(result, contacts)

        search = "some"
        self.session.query().filter().limit().offset().all.return_value = contacts
        result = await get_contacts(10, 0, search, self.user, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_id(self.contact_id, self.user, self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_unique_fields(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_unique_fields(self.body, self.user, self.session)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        result = await create_contact(self.body, self.user, self.session)
        self.assertEqual(result.firstname, self.body.firstname)
        self.assertEqual(result.lastname, self.body.lastname)
        self.assertEqual(result.email, self.body.email)
        self.assertEqual(result.phone, self.body.phone)
        self.assertEqual(result.birthday, self.body.birthday)
        self.assertEqual(result.description, self.body.description)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(
            self.body, self.contact_id, self.user, self.session
        )
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(
            self.contact_id, self.body, self.user, self.session
        )
        self.assertIsNone(result)

    async def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete_contact(self.contact_id, self.user, self.session)
        self.assertIsNone(result)

    async def test_delete_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await delete_contact(self.contact_id, self.user, self.session)
        self.assertEqual(result, contact)

    async def test_get_upcoming_birthdays(self):
        date = datetime.now() + timedelta(days=2)
        contacts = [
            Contact(
                birthday=datetime(1989, date.month, date.day),
            ),
            Contact(
                birthday=datetime(1989, date.month, date.day),
            ),
            Contact(
                birthday=datetime(1989, date.month, date.day),
            ),
        ]
        self.session.query().filter().limit().offset().all.return_value = contacts
        result = await get_upcoming_birthdays(self.user, self.session)
        self.assertEqual(result, contacts)

    async def test_get_upcoming_birthdays_no_birthdays(self):
        date = datetime.now() - timedelta(days=2)
        contacts = [
            Contact(
                birthday=datetime(1989, date.month, date.day),
            ),
            Contact(
                birthday=datetime(1989, date.month, date.day),
            ),
            Contact(
                birthday=datetime(1989, date.month, date.day),
            ),
        ]
        self.session.query().filter().limit().offset().all.return_value = contacts
        result = await get_upcoming_birthdays(self.user, self.session)
        self.assertEqual(result, [])
