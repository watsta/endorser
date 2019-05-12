import platform
import typing

_VERSION = platform.python_version().split(".")
_PY37 = _VERSION[0] is '3' and _VERSION[1] is '7'
_GENERIC_PARENT = typing._GenericAlias if _PY37 else typing.GenericMeta
_OPTIONAL_PARENT = typing._GenericAlias if _PY37 else typing._Union


def is_optional(attribute_type):
    """
    Checks whether the attribute is hinted with Optional type.

    :param attribute_type: the attribute to check
    :return: whether the attribute's type hint is optional or not
    """
    instance = isinstance(attribute_type, _OPTIONAL_PARENT)
    if _PY37 and instance:
        try:
            if attribute_type.__args__[1] is type(None):
                return True
        except IndexError:
            return False
    elif instance and attribute_type.__args__[1] is type(None):
        return True
    return False


def is_typing_list(attribute_type):
    """
    Checks whether the attribute is hinted with typing.List.

    :param attribute_type: the attribute to check
    :return: whether the attribute is hinted with typing.List
    """
    result = False
    if isinstance(attribute_type, _GENERIC_PARENT) :
        if _PY37 and attribute_type._name is 'List':
            result = True
        elif not _PY37 and issubclass(attribute_type, list):
            result = True
    return result
