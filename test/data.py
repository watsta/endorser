from typing import List, Optional

from endorser import Schema


class CustomSchema(Schema):
    str_prop: str


class ParentSchema(Schema):
    str_prop: str
    int_prop: int
    list_prop: list
    dict_prop: Optional[dict]
    custom_obj: CustomSchema
    typed_list_prop: List[str]
    typed_list_prop_with_custom_obj: List[CustomSchema]
    optional_with_default_value: Optional[str] = 'def'

    def validate_str_prop(self, value):
        return value


class InvalidSchema(Schema):
    invalid_prop = None
    str_prop: str
