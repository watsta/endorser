import platform
import typing

from endorser.util import construct_error

VERSION = platform.python_version().split(".")
PY37 = VERSION[0] is '3' and VERSION[1] is '7'
GENERIC_TYPE = typing._GenericAlias if PY37 else typing.GenericMeta


class Schema:

    def __new__(cls, **kwargs):
        """
        Collects mandatory fields into a list and binds it to the class.
        Only has to run once for every class, hence the `_processed` property.
        """
        if not hasattr(cls, '_processed'):
            mandatory_fields = []
            for k in cls.__annotations__.keys():

                # collect mandatory fields
                if not hasattr(cls, k):
                    mandatory_fields.append(k)

                # assign empty class variables from annotations
                # necessary to check for unknown attributes later on
                if not hasattr(cls, k):
                    setattr(cls, k, None)

            cls._mandatory_fields = mandatory_fields
            cls._processed = True

        return super(Schema, cls).__new__(cls)

    def __init__(self, _allow_unknown=False, **kwargs):
        """
        Initializes the `Schema` object, running provided validations.

        :param _allow_unknown: whether to allow unknown properties on the
            object
        """
        mandatory_fields = self._mandatory_fields.copy()
        self._instance_errors = []
        self._doc_errors = []

        class_items = self.__class__.__dict__
        # set attributes
        for k, v in kwargs.items():
            if not _allow_unknown:
                self._check_unknown_attributes(k)

            # remove provided attributes from the mandatory list
            # this is necessary to accept provided `None` values as well
            if k in mandatory_fields and v is not None:
                mandatory_fields.remove(k)

            # run validations
            validation_field = 'validate_%s' % k
            if validation_field in class_items:
                v = class_items[validation_field](self, v)

            # check if type matches the annotated type
            self._validate_type(k, v)

            setattr(self, k, v)

        # check if all mandatory fields have been set
        self._check_mandatory_fields(mandatory_fields)

    def _check_unknown_attributes(self, attr_name):
        """
        Checks for unknown attributes.

        :param attr_name: the attribute's name
        """
        if not hasattr(self, attr_name):
            self._instance_errors.append(
                construct_error(attr_name, "unknown attribute",
                                self.__class__.__name__))

    def _validate_type(self, attr_name, attr_val):
        """
        Validates the type of the property based on the annotation.

        :param attr_name: the name of the attribute
        :param attr_val: the value of the attribute
        """
        type_ = type(attr_val)
        try:
            annotated_type = self.__class__.__annotations__[attr_name]
        except KeyError:
            # KeyError means unknown attribute. Can only occur when
            # `_allow_unknown is True`
            return
        if attr_val is None:
            # if the value is None, it's type will be NoneType
            # we check for mandatory value assignment later
            pass
        elif type(annotated_type) is GENERIC_TYPE and \
                ((PY37 and annotated_type._name is 'List') or
                 (not PY37 and issubclass(annotated_type, list))):
            # check typing.List
            try:
                list_element_type = annotated_type.__args__[0]
                for i, elem in enumerate(attr_val):
                    if not type(elem) is list_element_type:
                        self._instance_errors.append(
                            construct_error(
                                attr_name, "wrong type in index %s. expected: "
                                           "'%s', provided: '%s'" %
                                           (i, list_element_type, type(elem)),
                                self.__class__.__name__)
                        )
                        break
            except (IndexError, TypeError):
                # if we get either of these exceptions it means that the
                # annotation is a generic List with no type hints for it's
                # content
                pass

        elif not type_ == annotated_type:
            self._instance_errors.append(
                construct_error(attr_name,
                                "wrong type. expected: '%s', provided: '%s'"
                                % (annotated_type.__name__, type_.__name__),
                                self.__class__.__name__))

    def _check_mandatory_fields(self, mandatory_fields):
        for mandatory in mandatory_fields:
            if getattr(self, mandatory) is None:
                self._instance_errors.append(
                    construct_error(mandatory,
                                    "mandatory field not set",
                                    self.__class__.__name__))

    @property
    def instance_errors(self):
        """
        :return: the validation errors on this object
        """
        return self._instance_errors

    @property
    def doc_errors(self):
        """
        Traverses every object in this instance (include self) and returns all
        validation errors.

        :return: validation errors for every object in this object including
            self
        """
        if self._doc_errors:
            return self._doc_errors

        errors = self._instance_errors
        for prop, val in vars(self).items():
            if issubclass(type(val), Schema):
                errors = errors + val.doc_errors
        self._doc_errors = errors
        return self._doc_errors

    def __repr__(self):
        class_dict = self.__class__.__dict__.copy()
        class_vars = {}
        for k, v in class_dict.items():
            if k[:1] != '_' and not callable(v):
                class_vars[k] = v
        class_vars.update(self.__dict__)
        return str(class_vars)
