from pydantic import ConfigDict, BaseModel

from constants.field_types.field_availability import FieldAvailability
from constants.field_types.field_representation import FieldRepresentation, DATA_TYPE_INDEX, POT_INDEX, \
    FIELD_REPRESENTATION_INDEX


class FieldOption(BaseModel):
    model_config = ConfigDict(slots=True, arbitrary_types_allowed=True)

    availability: FieldAvailability | None = None
    representation: list[FieldRepresentation] | FieldRepresentation | None = None
    # representation that is used for flat comparison
    comparison_representation: list[FieldRepresentation] | FieldRepresentation | None = None


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


    def get_representation_numbers(self, for_comparison: bool = False) -> None | list[int]:
        if self.representation is None:
            return None

        this_representation = self.comparison_representation if for_comparison else self.representation

        if isinstance(this_representation, FieldRepresentation):
            representation_list = [this_representation]
        else:
            representation_list = this_representation

        output = { }
        for representation in representation_list:
            for name_tuple in representation.get_named_product():
                if not self.is_available(name_tuple[DATA_TYPE_INDEX], name_tuple[POT_INDEX]):
                    continue

                value_tuple = FieldRepresentation.transform_tuple(name_tuple, to_int=False)
                code = value_tuple[DATA_TYPE_INDEX] + value_tuple[POT_INDEX]
                if code in output:
                    pass
                else:
                    output[code] = value_tuple[FIELD_REPRESENTATION_INDEX]

        return output if output else None


class RepresentationNumbersMixin:
    def get_representation_numbers(self, for_comparison: bool = False) -> None | list[int]:
        if self.field_options is None:
            return None

        return self.field_options.get_representation_numbers(for_comparison=for_comparison)
