import unittest
from typing import List

from endorser import ConversionError
from endorser import DocumentConverter
from test.data import ParentSchema, InvalidSchema


class ConverterTest(unittest.TestCase):
    A_STRING = "some string"
    A_STRING_2 = "another string"
    A_STRING_3 = "some string 2"
    A_STRING_4 = "another string 2"
    NOT_DEF_VAL = "not def value"

    def setUp(self):
        self.converter = DocumentConverter()
        self.VALID_DOCUMENT = {
            "str_prop": self.A_STRING,
            "int_prop": 123,
            "list_prop": ["some", 2, "values"],
            "custom_obj": {
                "str_prop": self.A_STRING_2
            },
            "typed_list_prop": ["has", "to", "be", "string"],
            "typed_list_prop_with_custom_obj": [{
                "str_prop": "values in a list 1"
            }, {
                "str_prop": "values in a list 2"
            }]
        }

        self.ANOTHER_DOCUMENT = {
            "str_prop": self.A_STRING_3,
            "int_prop": 321,
            "list_prop": [1, "value", 2],
            "custom_obj": {
                "str_prop": self.A_STRING_4
            },
            "typed_list_prop": ["string", "list"],
            "typed_list_prop_with_custom_obj": [{
                "str_prop": "values in a list 3"
            }, {
                "str_prop": "values in a list 4"
            }],
            "prop_with_default_value": self.NOT_DEF_VAL
        }

    def test_converter(self):
        result = self.converter.convert(self.VALID_DOCUMENT, ParentSchema)
        self.assertEqual(result.str_prop, self.A_STRING)
        self.assertEqual(result.custom_obj.str_prop, self.A_STRING_2)

    def test_converter_with_list(self):
        data = [self.VALID_DOCUMENT, self.ANOTHER_DOCUMENT]
        result = self.converter.convert(data, List[ParentSchema])

        self.assertEqual(2, len(result))
        self.assertEqual(result[0].str_prop, self.A_STRING)
        self.assertEqual(result[0].custom_obj.str_prop, self.A_STRING_2)
        self.assertEqual(result[0].prop_with_default_value,
                         ParentSchema.prop_with_default_value)
        self.assertEqual(result[1].str_prop, self.A_STRING_3)
        self.assertEqual(result[1].custom_obj.str_prop, self.A_STRING_4)
        self.assertEqual(result[1].prop_with_default_value, self.NOT_DEF_VAL)

    def test_converter_with_invalid_prop(self):
        prop = "int_prop"
        val = "string"
        self.VALID_DOCUMENT[prop] = val
        with self.assertRaises(ConversionError) as e:
            self.converter.convert(self.VALID_DOCUMENT, ParentSchema)
        self.assertEqual(1, len(e.exception.errors))
        self.assertEqual(e.exception.errors[0]['field'], prop)

    def test_schema_with_not_type_hinted_prop(self):
        with self.assertRaises(ValueError):
            self.converter.convert({'str_prop': 'str', 'invalid_prop': 123},
                                   InvalidSchema)
