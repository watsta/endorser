import typing
import unittest

from endorser import Schema


class TestSchema(unittest.TestCase):
    def test_mandatory_fields_property_value(self):
        class SchemaToTest(Schema):
            prop: int
            optional_prop: typing.Optional[int]
            optional_prop_with_default_value: typing.Optional[int] = 3
            list_prop: typing.List[str]

        schema = SchemaToTest(prop=3, list_prop=["10"])
        self.assertCountEqual(schema._mandatory_fields, ["prop", "list_prop"])

    def test_schema_creation_with_arguments(self):
        class SchemaToTest(Schema):
            prop: int

        with self.assertRaises(AttributeError):
            SchemaToTest(12)

    def test_mandatory_field_with_default_value(self):
        class SchemaToTest(Schema):
            prop: int = 10

        with self.assertRaises(AttributeError):
            SchemaToTest(prop=10)

    def test_optional_field_with_invalid_default_value(self):
        class SchemaToTest(Schema):
            prop: int = "invalid"

        with self.assertRaises(AttributeError):
            SchemaToTest(prop=0)

    def test_schema_creation_attribute_assignment(self):
        class SchemaToTest(Schema):
            prop: int
            optional_prop: typing.Optional[str]

        s = SchemaToTest(prop=0)
        self.assertIsNone(s.optional_prop)
