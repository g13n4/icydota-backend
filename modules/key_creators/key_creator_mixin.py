from typing import Any


APPEND_CONST = "___APPEND_CONST"


class KeyCreatorMixin:
    def get_fields(self):
        return self.fields


    def create_key(self, data: dict, fields: list[str] | None = None, *, append: Any = APPEND_CONST) -> tuple:
        """Get a dictionary and extract values from it according to the fields set"""
        fields_to_use = fields or self.fields
        output = [data[field] for field in fields_to_use]

        if append != APPEND_CONST:
            output.append(append)

        return tuple(output)


    def create_dict(self, data: dict, fields: list[str] | None = None) -> dict:
        """Get a dictionary and recreate using only required fields"""
        fields_to_use = fields or self.fields
        output = { field: data[field] for field in fields_to_use }

        return output
