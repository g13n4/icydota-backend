from pydantic import ConfigDict, BaseModel

from constants.performance.field_types.field_availability import FieldAvailability
from constants.performance.field_types.field_representation import FieldRepresentation


class FieldOption(BaseModel):
    model_config = ConfigDict(slots=True, arbitrary_types_allowed=True)

    availability: FieldAvailability | None = None
    representation: list[FieldRepresentation] | FieldRepresentation | None = None


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

        output = []
        for representation in representation_list:
            for name_tuple in representation.get_named_product():
                if not self.is_available(*name_tuple[1:3]):
                    continue

                output.append(FieldRepresentation.transform_tuple(name_tuple, to_int=True))

        return output if output else None


class RepresentationNumbersMixin:
    def get_representation_numbers(self) -> None | list[int]:
        if self.field_options is None:
            return None

        return self.field_options.get_representation_numbers()
