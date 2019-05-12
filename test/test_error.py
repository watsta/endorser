from endorser.error import construct_error
from unittest.mock import patch

FIELD_NAME = "field-name"
ERROR_NAME = "error-name"
MSG = "error-message"
CLASS_NAME = "error-class"

@patch("endorser.error.warnings")
def test_create_error(warnings):
    error = construct_error(
        field_name=FIELD_NAME,
        msg=MSG,
        class_name=CLASS_NAME,
        custom_error="test"
    )
    assert warnings.warn.called
    assert error['class'] == CLASS_NAME
    assert error['error'] == MSG
    assert error['custom_error'] == "test"


def test_create_error_without_class_name():
    error = construct_error(
        field_name=FIELD_NAME,
        msg=MSG,
        name=ERROR_NAME
    )
    assert error['name'] == ERROR_NAME
    assert error['error'] == MSG
