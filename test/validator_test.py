import unittest

from endorser import validator


class ValidatorTest(unittest.TestCase):
    FIELD_NAME = 'field_mock'

    def setUp(self):
        self.instance_errors = []

    def validation_field_mock(self, fun, val):
        return val

    def validation_field(self, fun, val):
        return val

    def test_not_none_validator(self):
        validator.not_none(self.validation_field_mock)(self, 'not_null')
        self.assertEqual([], self.instance_errors)

    def test_any_validator_with_validation_function_with_one_part(self):
        validator.not_none(self.validation_field)(self, None)
        self.assertEqual(1, len(self.instance_errors))
        self.assertEqual('ValidatorTest',
                         self.instance_errors[0].get('class'))
        self.assertEqual("field",
                         self.instance_errors[0].get("field"))

    def test_not_none_validator_with_null_val(self):
        validator.not_none(self.validation_field_mock)(self, None)
        self.assertEqual(1, len(self.instance_errors))
        self.assertEqual('ValidatorTest',
                         self.instance_errors[0].get('class'))
        self.assertEqual(self.FIELD_NAME,
                         self.instance_errors[0].get("field"))

    def test_not_empty_validator_with_empty_values(self):
        validator.not_empty(self.validation_field_mock)(self, '')
        validator.not_empty(self.validation_field_mock)(self, {})
        validator.not_empty(self.validation_field_mock)(self, [])
        validator.not_empty(self.validation_field_mock)(self, ())
        # check if 0 breaks it, it shouldn't
        validator.not_empty(self.validation_field_mock)(self, 0)
        self.assertEqual(4, len(self.instance_errors))
        self.assertEqual('ValidatorTest',
                         self.instance_errors[0].get('class'))
        self.assertEqual(self.FIELD_NAME,
                         self.instance_errors[0].get('field'))

    def test_not_empty_validator_with_not_empty_values(self):
        validator.not_empty(self.validation_field_mock)(self, 's')
        validator.not_empty(self.validation_field_mock)(self, {1: '1'})
        validator.not_empty(self.validation_field_mock)(self, [1])
        validator.not_empty(self.validation_field_mock)(self, (1, 2))
        self.assertEqual([], self.instance_errors)

    def test_min_size_validator(self):
        validator.min_size(5)(self.validation_field_mock)(self, '12345')
        validator.min_size(5)(self.validation_field_mock)(self, [1, 2, 3, 4, 5])
        validator.min_size(5)(self.validation_field_mock)(self, {1: 1, 2: 2,
                                                                 3: 3, 4: 4,
                                                                 5: 5})
        validator.min_size(5)(self.validation_field_mock)(self, (1, 2, 3, 4, 5))
        validator.min_size(-10)(self.validation_field_mock)(self, 'any')
        self.assertEqual([], self.instance_errors)

    def test_min_size_validator_with_invalid_value(self):
        validator.min_size(5)(self.validation_field_mock)(self, None)
        validator.min_size(5)(self.validation_field_mock)(self, '1234')
        validator.min_size(5)(self.validation_field_mock)(self, [1, 2, 3, 4])
        validator.min_size(5)(self.validation_field_mock)(self, {1: 1, 2: 2,
                                                                 3: 3, 4: 4})
        validator.min_size(5)(self.validation_field_mock)(self, (1, 2, 3, 4))
        self.assertEqual(5, len(self.instance_errors))
        self.assertEqual('ValidatorTest',
                         self.instance_errors[0].get('class'))
        self.assertEqual(self.FIELD_NAME,
                         self.instance_errors[0].get('field'))

    def test_max_size_validator(self):
        validator.max_size(3)(self.validation_field_mock)(self, '123')
        validator.max_size(3)(self.validation_field_mock)(self, [1, 2, 3])
        validator.max_size(3)(self.validation_field_mock)(self, {1: 1, 2: 2, 3: 3})
        validator.max_size(3)(self.validation_field_mock)(self, (1, 2, 3))
        self.assertEqual([], self.instance_errors)

    def test_max_size_validator_with_invalid_value(self):
        validator.max_size(3)(self.validation_field_mock)(self, None)
        validator.max_size(3)(self.validation_field_mock)(self, '1234')
        validator.max_size(3)(self.validation_field_mock)(self, [1, 2, 3, 4])
        validator.max_size(3)(self.validation_field_mock)(self, {1: 1, 2: 2,
                                                                 3: 3, 4: 4})
        validator.max_size(3)(self.validation_field_mock)(self, (1, 2, 3, 4))
        self.assertEqual(5, len(self.instance_errors))
        self.assertEqual('ValidatorTest',
                         self.instance_errors[0].get('class'))
        self.assertEqual(self.FIELD_NAME,
                         self.instance_errors[0].get('field'))

    def test_validate_uuid(self):
        validator.valid_uuid(self.validation_field_mock)(
            self, 'b0f07866-33bb-496c-98a8-49c040c1c18e')
        self.assertEqual([], self.instance_errors)

    def test_validate_uuid_with_invalid_value(self):
        validator.valid_uuid(self.validation_field_mock)(
            self, None)
        validator.valid_uuid(self.validation_field_mock)(
            self, 'invalid-uuid')
        validator.valid_uuid(self.validation_field_mock)(
            self, 123)
        validator.valid_uuid(self.validation_field_mock)(
            self, [1, 2, 3])
        validator.valid_uuid(self.validation_field_mock)(
            self, (1, 2))
        validator.valid_uuid(self.validation_field_mock)(
            self, object())
        self.assertEqual(6, len(self.instance_errors))
