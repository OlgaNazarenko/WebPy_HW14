# import sys
# import os
# import tracemalloc
#
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#
# import unittest
# from unittest.mock import MagicMock, AsyncMock
# from fastapi_mail import MessageSchema, MessageType, FastMail
#
# from sqlalchemy.orm import Session
#
# from src.services.auth import Auth
# from src.database.model import User
# from src.services.email import send_email
#
#
# class TestEmail(unittest.IsolatedAsyncioTestCase):
#     def setUp(self) :
#         self.session = MagicMock(spec=Session)
#         self.user = User(id = 1)
#         self.auth = Auth()
#
#     async def test_send_email(self) :
#         email="test@example.com"
#         username="test_user"
#         host="http://localhost:8000"
#
#         message = MessageSchema(
#             subject = "Confirm your email" ,
#             recipients = [email] ,
#             template_body = {"host" : host , "username" : username} ,
#             subtype = MessageType.html
#         )
#
#         token_verification = await self.auth.create_email_token({"sub" : email})
#         message = MessageSchema(
#             subject = "To confirm test" ,
#             recipients = [email] ,
#             template_body = {"host" : host , "username" : username, "token" : token_verification},
#             subtype = MessageType.html
#         )
#
#         fm_mock = AsyncMock(spec=FastMail)
#         fm_mock.send_message.return_value = True
#         self.auth.fm = fm_mock
#
#         send_message = await self.email.send_message(message, template_name = None)
#
#         self.assertTrue(fm_mock.send_message.called)
#         self.assertEqual(send_message, True)
#
# if __name__ == '__main__':
#     unittest.main()
