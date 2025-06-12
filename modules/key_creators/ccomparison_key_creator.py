from modules.key_creators.key_creator_mixin import KeyCreatorMixin
from modules.query_creators.const_map import CCOMPARISON_MODELS


class CrossComparisonPlayerKeyCreator(KeyCreatorMixin):
    def __init__(self, type_id: int):
        self.type_id = type_id
        self.models = CCOMPARISON_MODELS[type_id]
        self.fields = [item.field_name for item in self.models if not item.auxiliary]


class CrossComparisonTeamKeyCreator(KeyCreatorMixin):
    def __init__(self):
        self.fields = ['team_cpd_id', 'team_cps_id']
