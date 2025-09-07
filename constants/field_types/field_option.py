from pydantic import ConfigDict, BaseModel

from constants.field_types.field_availability import FieldAvailability
from constants.field_types.field_representation import FieldRepresentation, DATA_TYPE_INDEX, POT_INDEX, \
    FIELD_REPRESENTATION_INDEX, COMPARISON_INDEX, ComparisonTypeRepresentationEnum


class FieldOption(BaseModel):
    model_config = ConfigDict(slots=True, arbitrary_types_allowed=True)

    availability: FieldAvailability | None = None
    representation: list[FieldRepresentation] | FieldRepresentation | None = None

    is_comparable: bool = True


    def is_required(self, **kwargs) -> bool:
        if self.availability is None:
            return True

        return self.availability.is_required(**kwargs)


    def is_available(self, *args) -> bool:
        """
        :param args: names of the different types of calculations declared in FieldOption class
        :return: bool
        """
        if self.availability is None:
            return True

        return self.availability.is_available(*args)


    def get_representation_numbers(self) -> None | list[int]:
        if self.representation is None:
            return None

        if isinstance(self.representation, FieldRepresentation):
            representation_list = [self.representation]
        else:
            representation_list = self.representation

        output = { }
        for representation in representation_list:
            for name_tuple in representation.get_named_product():
                if not self.is_available(name_tuple[DATA_TYPE_INDEX], name_tuple[POT_INDEX]):
                    continue

                if not self.is_comparable and name_tuple[COMPARISON_INDEX] != ComparisonTypeRepresentationEnum.NONE:
                    continue

                value_tuple = FieldRepresentation.transform_tuple(name_tuple, to_int=False)
                code = value_tuple[DATA_TYPE_INDEX] + value_tuple[POT_INDEX] + value_tuple[COMPARISON_INDEX]
                field_code = value_tuple[FIELD_REPRESENTATION_INDEX]

                if code in output:
                    pass
                output[code] = field_code

        return output if output else None


class RepresentationNumbersMixin:
    def get_representation_numbers(self) -> None | list[int]:
        if self.field_options is None:
            return None

        return self.field_options.get_representation_numbers()
