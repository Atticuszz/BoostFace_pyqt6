# coding=utf-8

import re

from src.app.common.client import client


class AuthDialogM:
    def __init__(self):
        self.email: str = ''
        self.password: str = ''

    def login(self) -> bool:
        """
        login in with client
        """
        if client.login(self.email, self.password):
            return True
        else:
            return False

    def set_email(self, text: str):

        self.email = text

    def set_password(self, text: str):
        self.password = text

    def validate_email(self) -> bool:
        """email format validation"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, self.email) is not None

    def validate_password(self) -> bool:
        """
        Must have one uppercase letter, one lowercase letter, one number, and one symbol
        At least 8, at most 16 characters
        """
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#@!$%^&*])[A-Za-z\d#@!$%^&*]{8,16}$"
        return re.match(pattern, self.password) is not None
