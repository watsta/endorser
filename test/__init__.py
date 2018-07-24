from typing import List

from validation.schema import Schema


class CustomSchema(Schema):
    str_prop: str


class ParentSchema(Schema):
    str_prop: str
    int_prop: int
    list_prop: list
    custom_obj: CustomSchema
    typed_list_prop: List[str]
    typed_list_prop_with_custom_obj: List[CustomSchema]
    prop_with_default_value: str = 'def'

    def validate_str_prop(self, value):
        return value


class ChildSchema(ParentSchema):
    typed_list_prop: List
    new_prop: int
