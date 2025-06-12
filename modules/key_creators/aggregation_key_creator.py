from modules.key_creators.key_creator_mixin import KeyCreatorMixin
from modules.query_creators.const_map import AGGREGATION_MODELS


class AggregationPlayerKeyCreator(KeyCreatorMixin):
    def __init__(self, type_id: int | None = None, *, fields: list[str] | None = None):
        if type_id:
            self.type_id = type_id
            self.fields = [item.associated_field for item in AGGREGATION_MODELS[type_id]]
        elif fields:
            self.fields = fields
        else:
            raise ValueError("Can't create {self.__name__} without id for match or fields for team")


class AggregationTeamKeyCreator(KeyCreatorMixin):
    def __init__(self, fields: list[str] | None = None):
        self.fields = fields or ['team_id']
