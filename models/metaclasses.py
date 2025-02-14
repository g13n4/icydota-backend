from typing import Optional, ClassVar

from pydantic import condecimal
from sqlmodel import Field, SQLModel

from constants.performance.total import GameTotals, GameTotal
from constants.performance.window import AllWindows


class WindowMeta(type(SQLModel)):
    def __new__(cls, name, bases, dct, **kwargs):
        for attrib_name, annotation_type in AllWindows.__annotations__.items():
            game_window_value = getattr(AllWindows, attrib_name)
            if type(annotation_type) is AllWindows:
                # create it for pydantic
                setattr(cls, attrib_name, Field(default=None, nullable=True))
                cls.__annotations__[attrib_name] = condecimal(max_digits=10, decimal_places=2)
                # create it for const

                game_window_value.name = attrib_name

            cls.__annotations__['const'] = ClassVar[AllWindows]
            cls.const = AllWindows

        return super().__new__(cls, name, bases, dct, **kwargs)


class TotalMeta(type(SQLModel)):
    def __new__(cls, name, bases, dct, **kwargs):
        for attrib_name, annotation_type in GameTotals.__annotations__.items():
            if type(annotation_type) is GameTotal:
                cls_field_value = getattr(GameTotals, attrib_name)
                if annotation_type is condecimal:
                    # create it for pydantic
                    setattr(cls, attrib_name, Field(default=None, primary_key=True))
                    cls.__annotations__[attrib_name] = condecimal(
                        max_digits=cls_field_value.max_digits,
                        decimal_places=cls_field_value.decimal_places,
                    )
                else:
                    cls.__annotations__[attrib_name] = Optional[int]

                cls_field_value.name = attrib_name

        cls.__annotations__['const'] = ClassVar[GameTotals]
        cls.const = GameTotals

        return super().__new__(cls, name, bases, dct, **kwargs)
