import typing
import unittest

from endorser import DocumentConverter
from endorser import Schema
from endorser.validator import min_size


class Address(Schema):
    zip_code: str
    house_number: int
    addition: str = None


class User(Schema):
    email: str
    username: str
    firstname: typing.Optional[str]
    address: typing.Optional[Address]  # nest Schema classes

    @min_size(5)
    def validate_username(self, username):
        """Validates the username field, it has to be at least 5 chars long"""
        return username


data = {
    "email": "example@email.com",
    "username": "krisz",
    "address": {
        "zip_code": "6757",
        "house_number": 12,
        "addition": "A1"
    }
}


class BasicExampleTest(unittest.TestCase):

    def setUp(self):
        self.converter = DocumentConverter()

    def test_basic_example(self):
        user = self.converter.convert(data, User)
        assert user.email == "example@email.com"
        assert type(user.address) is Address
        assert user.address.zip_code == "6757"
