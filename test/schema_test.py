import unittest

from test.data import CustomSchema, ParentSchema


class TestSchema(unittest.TestCase):
    list_prop = [5, 6, 7]
    dict_prop = {"some": "dict"}
    int_prop = 123
    str_prop_1 = 'string_1'
    str_prop_2 = 'string_2'
    str_prop_3 = 'typed'
    str_prop_4 = 'list'
    test_schema_1 = CustomSchema(str_prop=str_prop_2)
    test_schema_2 = CustomSchema(str_prop='string_3')

    def setUp(self):
        self.PROPERTIES = {
            'str_prop': self.str_prop_1,
            'int_prop': self.int_prop,
            'list_prop': self.list_prop,
            'dict_prop': self.dict_prop,
            'custom_obj': self.test_schema_1,
            'typed_list_prop': [self.str_prop_3, self.str_prop_4],
            'typed_list_prop_with_custom_obj': [self.test_schema_2]
        }

    def test_correct_schema_creation(self):
        schema = ParentSchema(**self.PROPERTIES)

        self.assertEqual(schema.str_prop, self.str_prop_1)
        self.assertEqual(schema.int_prop, self.int_prop)
        self.assertEqual(schema.list_prop, self.list_prop)
        self.assertEqual(schema.dict_prop, self.dict_prop)
        self.assertEqual(schema.custom_obj, self.test_schema_1)
        self.assertCountEqual(schema.typed_list_prop, [self.str_prop_3,
                                                       self.str_prop_4])
        self.assertEqual(schema.typed_list_prop_with_custom_obj,
                         [self.test_schema_2])
        self.assertEqual(schema.prop_with_default_value, 'def')

    def test_updated_default_value(self):
        other_val = 'some_other_value'
        self.PROPERTIES['prop_with_default_value'] = other_val
        schema = ParentSchema(**self.PROPERTIES)

        self.assertEqual(schema.prop_with_default_value, other_val)

    def test_incorrect_type(self):
        invalid_prop = 'str_prop'
        self.PROPERTIES[invalid_prop] = 123
        schema = ParentSchema(**self.PROPERTIES)

        self.assertEqual(len(schema.doc_errors), 1)
        self.assertEqual(schema.doc_errors[0]['class'],
                         'ParentSchema')
        self.assertEqual(schema.doc_errors[0]['field'],
                         invalid_prop)

    def test_allow_unknown(self):
        unknown = 'unknown'
        unknown_val = 123
        self.PROPERTIES[unknown] = unknown_val
        self.PROPERTIES['_allow_unknown'] = True
        schema = ParentSchema(**self.PROPERTIES)
        self.assertEqual(schema.unknown, unknown_val)

    def test_nested_validation_errors(self):
        invalid_prop = 'str_prop'
        self.PROPERTIES[invalid_prop] = 123
        invalid_nested_prop = 'custom_obj'
        self.PROPERTIES[invalid_nested_prop] = CustomSchema(str_prop=456)
        schema = ParentSchema(**self.PROPERTIES)

        self.assertEqual(len(schema.doc_errors), 2)
        self.assertEqual(schema.doc_errors[0]['class'],
                         'ParentSchema')
        self.assertEqual(schema.doc_errors[0]['field'],
                         invalid_prop)
        self.assertEqual(schema.doc_errors[1]['class'],
                         'CustomSchema')
        self.assertEqual(schema.doc_errors[1]['field'],
                         invalid_prop)

    def test_mandatory_argument_with_None_provided(self):
        self.PROPERTIES['str_prop'] = None
        schema = ParentSchema(**self.PROPERTIES)

        self.assertEqual(len(schema.doc_errors), 1)
        self.assertEqual(schema.instance_errors[0]['class'], 'ParentSchema')
        self.assertEqual(schema.instance_errors[0]['field'], 'str_prop')

    def test_mandatory_argument_with_no_arg_provided(self):
        self.PROPERTIES.pop('str_prop')
        schema = ParentSchema(**self.PROPERTIES)

        self.assertEqual(len(schema.doc_errors), 1)
        self.assertEqual(schema.str_prop, None)
        self.assertEqual(schema.instance_errors[0]['class'], 'ParentSchema')
        self.assertEqual(schema.instance_errors[0]['field'], 'str_prop')
