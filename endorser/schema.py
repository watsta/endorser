from endorser.common import is_optional, is_typing_list
from endorser.error import construct_error, ErrorNames


class Schema:

    def __new__(cls, *args, **kwargs):
        """
        Collects mandatory fields into a list and binds it to the class.
        Only has to run once for every class, hence the `_processed` property.
        """
        if args:
            raise AttributeError("you can only use keyword arguments to "
                                 "instantiate a Schema object")

        if not hasattr(cls, '_processed'):
            optional_fields = []
            property_names = list(cls.__annotations__.keys())
            for property_name in property_names:
                annotated_type = cls.__annotations__[property_name]

                # collect optional fields
                if is_optional(annotated_type):
                    desired_type = annotated_type.__args__[0]
                    optional_fields.append(property_name)

                    # validate default value type
                    if hasattr(cls, property_name):
                        attr_value = getattr(cls, property_name)
                        cls._validate_type_hint(desired_type, attr_value)
                elif hasattr(cls, property_name):
                    raise AttributeError(
                        f"{property_name} has a default value and it's "
                        f"not an Optional.")

                # assign empty/None class variables from annotations
                # necessary to check for unknown attributes later on
                if not hasattr(cls, property_name):
                    setattr(cls, property_name, None)

            cls._mandatory_fields = [p for p in property_names
                                     if p not in optional_fields
                                     or property_names.remove(p)]
            cls._processed = True

        return super(Schema, cls).__new__(cls)

    @classmethod
    def _validate_type_hint(cls, desired_type, attr_value):
        if not isinstance(attr_value, (desired_type, type(None))):
            raise AttributeError(
                f"Optional type hinted with type "
                f"'{desired_type.__name__}' but got "
                f"'{type(attr_value).__name__}'")

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
            # remove provided attributes from the mandatory list
            # this is necessary to accept provided `None` values as well
            if k in mandatory_fields:
                mandatory_fields.remove(k)

                # run validations
                validation_field = 'validate_%s' % k
                if validation_field in class_items:
                    v = class_items[validation_field](self, v)

                self._validate_type(k, v, allow_unknown=_allow_unknown)

            setattr(self, k, v)

        # check if all mandatory fields have been set
        self._check_mandatory_fields(mandatory_fields)

    def _validate_type(self, attr_name, attr_val, allow_unknown):
        """
        Validates the type of the property based on the annotation.

        :param attr_name: the name of the attribute
        :param attr_val: the value of the attribute
        :param allow_unknown: whether to allow unknown attributes
        """
        type_ = type(attr_val)
        try:
            annotated_type = self.__class__.__annotations__[attr_name]
        except KeyError:
            # KeyError means unknown attribute. Can only occur when
            # `_allow_unknown is True`
            if not allow_unknown:
                self._instance_errors.append(
                    construct_error(attr_name, "unknown attribute",
                                    self.__class__.__name__,
                                    name=ErrorNames.UNKNOWN_ATTRIBUTE.value))
            return
        if is_typing_list(annotated_type):
            self._validate_typing_list(attr_name, attr_val)
        elif is_optional(annotated_type):
            self._validate_optional_type(attr_name, attr_val)
        elif not type_ == annotated_type:
            self._instance_errors.append(
                construct_error(attr_name,
                                "wrong type. expected: '%s', provided: '%s'"
                                % (annotated_type.__name__, type_.__name__),
                                self.__class__.__name__,
                                name=ErrorNames.WRONG_TYPE.value))

    def _validate_typing_list(self, attr_name, attr_val):
        annotated_type = self.__class__.__annotations__[attr_name]
        list_element_type = annotated_type.__args__[0]

        for i, elem in enumerate(attr_val):
            if not isinstance(elem, list_element_type):
                self._instance_errors.append(
                    construct_error(
                        attr_name, "wrong type in index %s. expected: "
                                   "'%s', provided: '%s'" %
                                   (i, list_element_type, type(elem)),
                        self.__class__.__name__,
                        name=ErrorNames.WRONG_TYPE.value)
                )
                break

    def _validate_optional_type(self, attr_name, attr_val):
        annotated_type = self.__class__.__annotations__[attr_name]
        desired_type = annotated_type.__args__[0]

        if not isinstance(attr_val, desired_type):
            construct_error(
                attr_name,
                f"wrong type. expected: '{annotated_type.__name__}', "
                f"provided: {type(attr_val).__name__}",
                self.__class__.__name__,
                name=ErrorNames.WRONG_TYPE.value)

    def _check_mandatory_fields(self, mandatory_fields):
        for mandatory in mandatory_fields:
            if getattr(self, mandatory) is None:
                self._instance_errors.append(
                    construct_error(mandatory,
                                    "mandatory field not set",
                                    self.__class__.__name__,
                                    name=ErrorNames.MANDATORY_FIELD_NOT_SET
                                    .value))

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
