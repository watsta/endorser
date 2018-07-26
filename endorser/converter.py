from typing import get_type_hints, TypeVar, Type, Union, List

from endorser.schema import Schema

S = TypeVar('S', dict, list)
T = TypeVar('T', bound=Schema)


class ConversionError(Exception):
    """Exception to raise when conversion fails."""

    def __init__(self, errors: list):
        self.errors = errors


class DocumentConverter:
    """
    Converter class to convert documents to typed objects.
    """

    def convert(self, document: S, doc_type: Union[Type[T], Type[List[T]]],
                allow_unknown=False) -> Union[T, List[T]]:
        """
        Converts an S from type list/dict to Type[T]/Type[List[T]].

        :param document: the object to convert
        :param doc_type: the class to convert to
        :param allow_unknown: whether to allow unknown values to be present
        :return: a populated class with type T
        """
        if not document:
            raise ValueError('empty document provided')

        if type(document) is dict:
            data = _transform_dict(document, doc_type, allow_unknown)
            if data.doc_errors:
                raise ConversionError(data.doc_errors)
        elif type(document) is list:
            data = _transform_list(document, doc_type, allow_unknown)
            errors = []
            for obj in data:
                if obj.doc_errors:
                    errors = errors + obj.doc_errors
            if errors:
                raise ConversionError(errors)
        else:
            raise TypeError('%s type cannot be converted, it has to be either'
                            'a list or a dict' % str(type(document)))
        return data


def _transform_dict(document: dict, doc_type: Type[T],
                    allow_unknown: bool) -> T:
    """
    Transforms the document from dict to type T.

    :param document: the data to transform
    :param doc_type: the class to transform to
    :return: the transformed object
    """
    hints = get_type_hints(doc_type)
    for k, v in document.items():
        if k not in hints:
            raise ValueError('%s is not type hinted' % k)

        if type(v) is dict:
            document[k] = _transform_dict(v, hints[k], allow_unknown)
        elif type(v) is list:
            try:
                document[k] = _transform_list(
                    v, hints[k], allow_unknown)
            except (IndexError, TypeError, AttributeError):
                # if we get either of these exceptions it means that the
                # annotation is a generic list with no type hints for it's
                # content, so we'll leave the content as it is.
                pass
    return doc_type(_allow_unknown=allow_unknown, **document)


def _transform_list(document: list, doc_type: Type[T],
                    allow_unknown: bool) -> List[T]:
    """
    Transforms the document from list to type T.

    :param document: the data to transform
    :param doc_type: the class to transform to
    :return: the transformed object
    """
    try:
        type_ = doc_type.__args__[0]
    except TypeError:
        raise TypeError('generic List type cannot be used as document type, '
                        'provide a type for the content of the list as well')
    return [_transform_dict(obj, type_, allow_unknown) for obj in
            document]
