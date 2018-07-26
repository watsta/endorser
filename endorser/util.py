

def construct_error(field_name: str,
                    error: str,
                    class_name: str=None, **kwargs) -> dict:
    """
    Constructs an error from the given params.

    :param field_name: the name of the field which failed the validation
    :param error: the error message about how the validation failed
    :param class_name: the name of the class, optional
    :param kwargs: any additional keyword arguments which will be added to the
        response dict
    :return: an error dict
    """
    error = {'field': field_name, 'error': error}
    if class_name:
        error['class'] = class_name
    if kwargs:
        for k, v in kwargs:
            error[k] = v
    return error
