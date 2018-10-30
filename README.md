# Endorser

[![codecov](https://codecov.io/gh/watsta/endorser/branch/master/graph/badge.svg)](https://codecov.io/gh/watsta/endorser)

A lightweight data validation and converter package for Python 3.6+.
It's always better to work with a structured set of data instead of just a simple dictionary. This package provides an easy way to do the conversion seamlessly while it provides a set of tools to validate the data.
The main purpose of this package is to create structured data from unstructured types while validating it.

```Python
from endorser import DocumentConverter
from endorser import Schema
from endorser import min_size

class Address(Schema):
    zip_code: str
    house_number: int
    addition: str = None

class User(Schema):
    email: str
    username: str
    firstname: str = None  # assigning None as default makes it optional during instantiation
    address: Address = None  # nest Schema classes

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

converter = DocumentConverter()
user = converter.convert(data, User) # converts the data dictionary to a User object
assert type(user) is User
assert user.email is "example@email.com"
assert type(user.address) is Address
assert user.address.zip_code is "6757"

```

## Install
Endorser is hosted on PyPI, you can install it via pip:
```
pip install endorser
```
To run the tests:
```
python setup.py install
python setup.py test
```
Endorser doesn't have any dependencies outside of pytest and pytest-runner.

## Features

### endorser.Schema
Base class for documents. 
* Must not be instantiated directly
* Every attribute must be type hinted
* As of now, supported type hints are the primivites, list, dict, typing.List and subclasses of Schema
* Every subclass of `Schema` must be considered as final and immutable
```Python
class User(Schema):
    email: str
    username: str
    firstname: str = None  # assigning None as default makes it optional
    age: int = 0  # assigning anything will be used as default value
    address: Address = None  # must be an instance of Schema
```
Note that it's possible for every attribute to have `None` as it's value, the default `None` only means that the value can be omitted from the document. If you want to make sure that the value cannot be `None`, apply the `@validator.not_none` decorator:
```Python
class User(Schema):
    email: str
    username: str = None
    
user = User(email="some@email.com")  # valid, as username can be omitted
user = User(email=None)  # valid, as email can have the value None

    ...
    from endorser.validator import not_none
    
    @not_none
    def validate_email(self, email):
        return email
        
user = User(email=None)  # not valid, as it's both mandatory and cannot be None
```

### Validation
You can validate `Schema` objects with following this convention:
```Python
from endorser import min_size

class SomeDocument(Schema):
    some_prop: str
    
    @min_size(5)  # has to be at least 5 chars long
    def validate_some_prop(self, value):
        return value
    
```
Every validation method has to start with the `validate_` prefix followed by the name of the property. The value argument is the value which will be set during instantiation. The method has to return the value as we set this value on the object.
You can see all validation methods in the `endorser.validator` package.

### Custom validation
You can either create a new decorator and apply it on the validator (for examples see the `endorser.validator` package) or apply the validation on the validation method itself.
```Python
from endorser.util import construct_error

class SomeDocument(Schema):
    some_prop: str
    
    @some_custom_validator  # apply custom decorators
    def validate_some_prop(self, value):
        for c in value:
            if c is " ":
                self.instance_errors.append(construct_error(
                    "some_prop", "cannot contain spaces"))
        return value  # make sure to always return the value
```

### Alter values
It's possible to alter the value of `Schema` objects during validation:
```Python
import uuid
from endorser import valid_uuid

class User(Schema):
    id: uuid.UUID
    email: str
    username: str = None
    
    @valid_uuid  # ensures that the ID is a valid UUID
    def validate_id(self, id): 
        return uuid.UUID(id)

user = User(id="7b4f95e3-4fbe-4f94-838f-c34950240274", 
            email="some@email.com")
assert isinstance(user.id, uuid.UUID)
```
You can also create custom decorators to modify property values. Note that we hinted the `id` property to be of type `uuid.UUID` but we instantiate it with a string value. You are responsible to return the correct value type which you defined on the `Schema` class.

### Instantiation
You have to use keyword arguments to instantiate a `Schema` object:
```Python
user = User(email="some@email.com", username="krisz")
```

You can set the `_allow_unknown` property on any `Schema` object to allow unknown properties:
```Python
user = User(_allow_unknown=True, email="some@email.com", unknown_prop="any value")
assert user.unknown_prop == "any value"
```

Validation happens during the instantiation of the `Schema` object. Note that there aren't any exception raised, you have to check if there were any errors yourself:
```Python
import uuid
from endorser import valid_uuid

class User(Schema):
    id: uuid.UUID
    email: str
    username: str = None
    
    @valid_uuid  # ensures that the ID is a valid UUID
    def validate_id(self, id): 
        return uuid.UUID(id)

user = User(id="invalid-uuid", 
            email="some@email.com")
assert user.id == "invalid-uuid"
if user.instance_errors:
    for error in user.instance_errors:
        print("invalid value for property %s: %s" % (error["field"], error["error"]))
```
You can use the `obj.instance_errors` property to check for errors on the instance and `obj.doc_errors` to check for validation errors on the whole document. This means if you have nested `Schema` objects, this property will return every error on every object from the root object:
```Python
from endorser import Schema
from endorser.validator import min_size

class Address(Schema):
    zip_code: str
    house_number: int
    addition: str = None

class User(Schema):
    email: str
    username: str
    firstname: str = None 
    address: Address = None

    @min_size(5)
    def validate_username(self, username):
        return username
    
user = User(email="some@email.com", username="Joe", 
            address=Address(zip_code="67ZZ", 
            house_number="invalid_type"))  # validation fails on username and house_number
assert len(user.instance_errors) == 1
assert len(user.address.instance_errors) == 1
assert len(user.doc_errors) == 2
```

### DocumentConverter
The DocumentConverter class is used to build structured data from a document. A document can either be a dictionary or a list of dictionaries. The DocumentConverter uses the `Schema` class to validate and build the objects from the document.
```Python
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
    firstname: str = None
    address: Address = None

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

converter = DocumentConverter()
user = converter.convert(data, User)
assert type(user) is User
assert user.email is "example@email.com"
assert type(user.address) is Address
assert user.address.zip_code is "6757"
```
The `DocumentConverter#convert` method raises a `ConversionError` if validation fails. It holds the error messages in the `ConversionError.errors` list.
You can pass the `allow_unknown=True` property to the `convert` method to allow unknown properties:
```Python
class SomeClass(Schema):
    prop: str
data = {
    "prop": "some property",
    "unknown_prop": "not defined on the class"
}

converter = DocumentConverter()
some_obj = converter.convert(data, SomeClass, allow_unknown=True)
assert some_obj.unknown_prop == "not defined on the class"
```
You can also pass a list of objects to the converter:
```Python
data = [{
        "prop": "a property"
    }, {
        "prop": "another property"
}]
    
list_of_objs = converter.convert(data, List[SomeClass])
assert type(list_of_objs) is list
assert type(list_of_objs[0]) is SomeClass
assert len(list_of_objs) == 2
```

### Examples
For more examples see the `test.example` package.

### Limitations
* Only works on Python 3.6+
* Currently supported types are all primitives, list, dict and typing.List, and of course other Schema objects as well
* Classes which inherit from Schema are effectively final, you must not inherit from them