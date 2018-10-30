import warnings
from enum import Enum


def construct_error(field_name: str,
                    error: str,
                    class_name: str=None,
                    name: str = None, **kwargs) -> dict:
    """
    Constructs an error from the given params.

    :param field_name: the name of the field which failed the validation
    :param error: the error message about how the validation failed
    :param class_name: the name of the class, optional
    :param name: a unique name of the error
    :param kwargs: any additional keyword arguments which will be added to the
        response dict
    :return: an error dict
    """
    if not name:
        warnings.warn("do not construct an error message without the name "
                      "param, later it will be mandatory",
                      category=DeprecationWarning)

    error = {'field': field_name, 'error': error}

    if name:
        error['name'] = name
    if class_name:
        error['class'] = class_name
    if kwargs:
        for k, v in kwargs:
            error[k] = v
    return error


class ErrorNames(Enum):
    NONE_VALUE = "NONE_VALUE"
    EMPTY_VALUE = "EMPTY_VALUE"
    MIN_SIZE_NOT_REACHED = "MIN_SIZE_NOT_REACHED"
    MAX_SIZE_EXCEEDED = "MAX_SIZE_EXCEEDED"
    INVALID_UUID = "INVALID_UUID"
    MANDATORY_FIELD_NOT_SET = "MANDATORY_FIELD_NOT_SET"
    WRONG_TYPE = "WRONG_TYPE"
    UNKNOWN_ATTRIBUTE = "UNKNOWN_ATTRIBUTE"

