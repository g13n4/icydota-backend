from pydantic import BaseModel, ConfigDict


class FieldAvailability(BaseModel):
    model_config = ConfigDict(slots=True)

    __match_args__ = ("match", "aggregation", "cross_comparison")

    match: bool = True
    aggregation: bool = True
    cross_comparison: bool = True

    player: bool = True
    team: bool = True
    # weather availability rule works if any field is matched (or)
    # or all fields should be matched for a rule to be applied (and)
    for_any_option: bool = True

    is_hidden: bool = False


    def is_required(self, **kwargs) -> bool:
        """If a value is required it should present during output. If it's not it should be removed"""
        for k, v in kwargs:
            try:
                availability_value = getattr(self, k)
            except AttributeError:
                raise AttributeError(f"Wrong required type {k} with value {v} in {self.__name__}")

            if not (availability_value and v):
                return False
        return True


    def is_available(self, *args) -> bool:
        """
        :param args: names of the different types of calculations declared in FieldOption class
        :return: bool
        """
        if self.is_hidden:
            return False

        if self.for_any_option:
            for field in args:
                # only every field should be matched for restriction not to trigger
                if not getattr(self, field):
                    return False
            return True
        else:
            availability_list = [getattr(self, field) for field in args]
            # return True if no args provided
            # only one field should be true for restriction not to trigger
            return any(availability_list) if availability_list else True
