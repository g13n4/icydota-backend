from typing import ClassVar, TypeVar, Any
from pydantic import BaseModel

Constant = TypeVar("Constant")


class Item(BaseModel):
    value: Any
    name: str = ''
    description: str = ''


    def __eq__(self, other):
        is_eq_value = isinstance(other, int) and self.value == other
        is_eq_name = isinstance(other, str) and self.name == other

        return (super().__eq__(other) or is_eq_value or is_eq_name)


def include_CV_types(types: list[Any]) -> list[Any]:
    """
    Adds ClassVar to types provided in a list
    """
    new_types = []
    for type_ in types:
        new_types.append(ClassVar[type_])

    return types + new_types


def to_description(text: str) -> str:
    split_text = text.split('_')
    return ' '.join(x.lower().capitalize() for x in split_text)


def to_nested_constant(klass: Constant) -> Constant:
    # turn every class variable into an object that contains: description, value and system name
    values = []
    for name, type_ in klass.__annotations__.items():
        if type_ in include_CV_types([int, bool, ]):
            value = getattr(klass, name)
            description = to_description(name)

        elif type_ in include_CV_types([tuple, tuple[int, str], ]):
            value, description = getattr(klass, name)

        elif type_ in [dict, list, ]:
            continue

        else:
            raise NotImplementedError("Behaviour for this type is not implemented.")


        constant_data = Item(value=value, name=name, description=description)
        values.append(constant_data)
        setattr(klass, name, constant_data)

    setattr(klass, 'VALUES', values)

    return klass


def update_description(klass: Constant) -> Constant:
    for name, type_ in klass.__annotations__.items():
        try:
            if issubclass(Item, type_):
                item = getattr(klass, name)
                if not item.name:
                    item.name = name

                if not item.description:
                    description = to_description(name)
                    item.description = description
        except TypeError:  # generics can't be checked with issubclass
            continue

    return klass



def get_only_names(items: list[BaseModel]) -> list[str]:
    return [item.name for item in items]


class GetItemHelper:
    def __class_getitem__(cls, key: str) -> Item:
        return getattr(cls, key)


def sec_to_min(value: int) -> str:
    return f"{value / 60:.1f} min."


def to_range(value1: int, value2: int) -> str:
    return " - ".join(map(sec_to_min, [value1, value2]))

