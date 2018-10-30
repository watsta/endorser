import functools
import uuid

from endorser.error import construct_error, ErrorNames


def not_none(validation_field):
    """
    Checks whether a value is None
    """

    @functools.wraps(validation_field)
    def validator(self, value):
        prop_name = _get_property_name_from(validation_field)
        if value is None:
            self.instance_errors.append(
                construct_error(prop_name,
                                'None value',
                                self.__class__.__name__,
                                name=ErrorNames.NONE_VALUE.value))
        return validation_field(self, value)

    return validator


def not_empty(validation_field):
    """
    Checks whether a value is empty (which is either None or an empty value).
    """

    @functools.wraps(validation_field)
    def validator(self, value):
        prop_name = _get_property_name_from(validation_field)
        if not value and value is not 0:
            self.instance_errors.append(
                construct_error(prop_name,
                                'empty value',
                                self.__class__.__name__,
                                name=ErrorNames.EMPTY_VALUE.value))
        return validation_field(self, value)

    return validator


def min_size(size: int):
    """Checks whether the value has the minimum size (<)."""

    def decorator(validator_function):
        def validator(self, value):
            prop_name = _get_property_name_from(validator_function)
            if not value or len(value) < size:
                self.instance_errors.append(
                    construct_error(prop_name,
                                    'minimum size %d not reached' % size,
                                    self.__class__.__name__,
                                    name=ErrorNames.MIN_SIZE_NOT_REACHED
                                    .value))
            return validator_function(self, value)

        return validator

    return decorator


def max_size(size: int):
    """Checks whether the value has the maximum size (>)."""

    def decorator(validator_function):
        def validator(self, value):
            prop_name = _get_property_name_from(validator_function)
            if not value or len(value) > size:
                self.instance_errors.append(
                    construct_error(prop_name,
                                    'maximum size %d exceeded' % size,
                                    self.__class__.__name__,
                                    name=ErrorNames.MAX_SIZE_EXCEEDED.value))
            return validator_function(self, value)

        return validator

    return decorator


def valid_uuid(validation_field):
    """
    Checks whether the value is a valid UUID.
    """

    @functools.wraps(validation_field)
    def validator(self, value):
        prop_name = _get_property_name_from(validation_field)
        try:
            uuid.UUID(value)
        except (ValueError, AttributeError, TypeError):
            self.instance_errors.append(
                construct_error(prop_name,
                                '{} is not a valid uuid'.format(value),
                                self.__class__.__name__,
                                name=ErrorNames.INVALID_UUID.value))
        return validation_field(self, value)

    return validator


def _get_property_name_from(fn):
    return fn.__name__.split('_', 1)[1]
