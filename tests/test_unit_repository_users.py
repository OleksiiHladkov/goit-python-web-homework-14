import asyncio
import unittest
from unittest.mock import MagicMock
from datetime import datetime


from sqlalchemy.orm import Session


from contacts_book.database.models import User
from contacts_book.schemas import UserModel
from contacts_book.repository.users import get_user_by_email, create_user, update_avatar, update_token, confirmed_email 


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.body = UserModel(
            username = "Python student",
            email = "pythonstudent@ex.ua",
            password = "123456"
        )
        self.user_id = 1

    async def test_get_user_by_email(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(self.body.email, self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        result = await create_user(self.body, self.session)
        self.assertEqual(result.username, self.body.username)
        self.assertEqual(result.email, self.body.email)
        self.assertEqual(result.password, self.body.password)
        self.assertTrue(hasattr(result, "id"))
    
    async def test_update_token(self):
        user = User()
        token = "dflgkjdfkgkdfg"
        result = await update_token(user, token, self.session)
        self.assertEqual(result, None)
    
    async def test_confirmed_email_user_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await confirmed_email(self.body.email, self.session)
        self.assertIsNone(result)

    async def test_confirmed_email_user_found(self):
        user = User()
        self.session.query().filter().first.return_value = user
        self.session.commit.return_value = None
        result = await confirmed_email(self.body.email, self.session)
        self.assertEqual(result, None)
    
    async def test_update_avatar_user_not_found(self):
        url = "www"
        self.session.query().filter().first.return_value = None
        result = await update_avatar(self.body.email, url, self.session)
        self.assertIsNone(result)

    async def test_update_avatar_user_found(self):
        user = User()
        url = "www"
        self.session.query().filter().first.return_value = user
        self.session.commit.return_value = None
        result = await update_avatar(self.body.email, url, self.session)
        self.assertEqual(result, user)
