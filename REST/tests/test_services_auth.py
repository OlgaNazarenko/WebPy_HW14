import sys
import os
import tracemalloc

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from src.services.auth import Auth
from src.database.model import User
from src.conf.messages import UNAUTHORIZED


class TestAuth(unittest.IsolatedAsyncioTestCase):
    def setUp(self) :
        self.session = MagicMock(spec = Session)
        self.user = User(id = 1)
        self.auth = Auth()

    async def test_verify_password(self):
        plain_password = 'test_password'
        hashed_password = self.auth.pwd_context.hash("test_password")
        result = self.auth.verify_password(plain_password, hashed_password)
        self.assertTrue(result)

    async def test_password_hash(self):
        password = "test"
        password_hash = self.auth.get_password_hash("password")
        self.assertTrue(password_hash)
        self.assertNotEqual(password_hash, password)

    async def test_create_access_token(self):
        data = {"sub" : "1234567890" , "name" : "test" , "iat" : 1516239022}
        token = await self.auth.create_access_token(data , expires_delta = 3600)
        self.assertTrue(isinstance(token, str))

    async def test_create_refresh_token(self):
        data = {"sub" : "1234567890" , "name" : "test2", "iat" : 1516239022}
        token = await self.auth.create_refresh_token(data, expires_delta = 3600)
        self.assertTrue(isinstance(token , str))

    async def test_decode_refresh_token(self):
        test_email = "test@gmail.com"
        refresh_token = await self.auth.create_refresh_token({'sub': test_email})
        decoded_token = await self.auth.decode_refresh_token(refresh_token)
        self.assertEqual(decoded_token, test_email)

    def tearDown(self) :
        tracemalloc.stop()

if __name__ == '__main__':
    unittest.main()
