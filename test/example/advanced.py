import unittest
from typing import List

from endorser import construct_error
from endorser.converter import DocumentConverter
from endorser.schema import Schema
from endorser.validator import min_size, not_empty, max_size


class Hobby(Schema):
    name: str


class Phone(Schema):
    number: str

    @not_empty
    def validate_number(self, number):
        for c in number:
            if not c.isdigit():
                self.instance_errors.append(construct_error(
                    'number',
                    'can only contain digits',
                    self.__class__.__name__
                ))
        return number


class Address(Schema):
    zip_code: str
    address_name: str = None
    phone: Phone = None

    def validate_zip_code(self, zip_code):
        if len(zip_code) != 4:
            self.instance_errors.append(construct_error(
                'zip_code',
                'zip code must be 4 chars long',
                self.__class__.__name__
            ))
        return zip_code

    @not_empty
    def validate_address_name(self, address):
        """
        This way address_name is optional but if it's present it cannot be
        empty.
        """
        return address


class UserRegistration(Schema):
    email: str
    password: str
    first_name: str
    last_name: str = None
    address: Address
    hobbies: List[Hobby]

    @min_size(5)
    def validate_email(self, value):
        return value

    @not_empty
    def validate_hobbies(self, hobbies):
        return hobbies

    @max_size(30)
    def validate_password(self, pw):
        self._secret_password = pw
        return "HIDDEN"

    @not_empty
    def validate_last_name(self, last_name):
        return last_name


data = [{
    "email": "some@email.com",
    "password": "some_password",
    "first_name": "Krisztian",
    "address": {
        "zip_code": "3023",
        "address_name": "Wonderland",
        "phone": {
            "number": "061222329"
        }
    },
    "hobbies": [{
        "name": "existing"
    }, {
        "name": "getting tired"
    }]
}]


class AdvancedExampleTest(unittest.TestCase):

    def setUp(self):
        self.converter = DocumentConverter()

    def test_advanced_example(self):
        users = self.converter.convert(data, List[UserRegistration])
        user = users[0]
        assert user.email == "some@email.com"
        assert type(user.address) is Address
        assert type(user.address.phone) is Phone
        assert user.address.zip_code == "3023"
        assert user._secret_password == "some_password"
        assert user.password == "HIDDEN"
