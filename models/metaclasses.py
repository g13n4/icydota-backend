from typing import Optional, ClassVar

from pydantic import condecimal
from sqlmodel import Field, SQLModel
from constants.performance.total import GameTotals
from constants.performance.window import GameWindows


class WindowMeta(type(SQLModel)):
    def __new__(cls, name, bases, dct, **kwargs):
        # setting const and fields for the class
        # ClassVar for const object and filling fields
        cls.const = type('Const', (object,), {})
        cls.__annotations__['const'] = ClassVar[object]

        for name, annotation_type in GameWindows.__annotations__.items():
            game_window_value = getattr(GameWindows, name)
            if isinstance(annotation_type, GameWindows):
                # create it for pydantic
                setattr(cls, name, Field(default=None, nullable=True))
                cls.__annotations__[name] = condecimal(max_digits=10, decimal_places=2)
                # create it for const

                game_window_value.name = name

            setattr(cls.const, name, game_window_value)
            cls.const.__annotations__[name] = annotation_type

        return super().__new__(cls, name, bases, dct, **kwargs)


class TotalMeta(type(SQLModel)):
    def __new__(cls, name, bases, dct, **kwargs):
        # setting const and fields for the class
        # ClassVar for const object and filling fields
        cls.const = type('Const', (object,), {})
        cls.__annotations__['const'] = ClassVar[object]

        counter = 1
        values = []
        for name, annotation_type in GameTotals.__annotations__.items():
            cls_field_value = getattr(GameTotals, name)
            if annotation_type is condecimal:
                # create it for pydantic
                setattr(cls, name, Field(default=None, primary_key=True))
                cls.__annotations__[name] = condecimal(
                    max_digits=cls_field_value.max_digits,
                    decimal_places=cls_field_value.decimal_places,
                )
            else:
                cls.__annotations__[name] = Optional[int]
            values.append(name)

            cls_field_value.name = name
            counter += 1

            setattr(cls.const, name, cls_field_value)
            cls.const.__annotations__[name] = annotation_type

        setattr(cls.const, 'VALUES', values)

        return super().__new__(cls, name, bases, dct, **kwargs)
