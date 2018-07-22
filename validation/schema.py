class Schema:

    def __new__(cls, **kwargs):
        if not hasattr(cls, '_processed'):
            mandatory_fields = []
            for k in cls.__annotations__.keys():
                var_name = '_%s' % k

                # collect mandatory fields
                # since we shadow class variables with properties we have
                # to check whether the attribute is a property or not
                if not hasattr(cls, k) or \
                        isinstance(getattr(cls, k), property):
                    mandatory_fields.append(k)

                # reassign variables to private variables
                setattr(cls, var_name, None)

            cls._mandatory_fields = mandatory_fields
            cls._processed = True

        return object.__new__(cls)

    def __init__(self, **kwargs) -> None:
        mandatory_fields = self._mandatory_fields.copy()
        annotations = self.__class__.__annotations__

        # set attributes
        for k, v in kwargs.items():
            var_name = '_%s' % k
            if not hasattr(self, var_name):
                raise AttributeError("%s has no attribute '%s'" %
                                     (self.__class__, k))

            type_ = type(v)
            annotated_type = annotations[k]
            if not type_ == annotated_type:
                raise AttributeError("%s has the wrong type. expected: '%s',"
                                     "provided: '%s'" %
                                     (k, annotated_type, type_))

            setattr(self, var_name, v)

            # remove provided attributes from the mandatory list
            # this is necessary to accept provided `None` values as well
            if k in mandatory_fields:
                mandatory_fields.remove(k)

        # check if all mandatory fields have been set
        for mandatory in mandatory_fields:
            if getattr(self, mandatory) is None:
                raise AttributeError("%s was not set but is mandatory"
                                     % mandatory)

    def __repr__(self):
        return str(self.__dict__)
