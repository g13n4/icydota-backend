from constants.calculation.cross_comparison import CrossComparisonTypeConstant
from modules.minmax_finder import TableMinMaxFinder
from modules.query_creators.const_map import CCOMPARISON_MODELS
from utils import is_na_decimal


SENTINEL = object


class CrossComparisonProcessor:
    REPLACEMENT_MAP = {
        "player_cpd_id": "player",
        "team_cpd_id": "team",
    }


    def __init__(self, ccomp_type: int, TMMF: TableMinMaxFinder, custom_expected: list[str]):
        self.ccomp_type = ccomp_type
        self.TMMF = TMMF

        match self.ccomp_type:
            case None:
                self.name = "Team"
                self.fields_key = ["team_cpd_id", ]
                self.fields_value = ["team_cps_id", ]
                self.expected_values = custom_expected[1:]  # excluding value which always go first

            case CrossComparisonTypeConstant.POSITION_PLAYER:
                self.name = "Player"
                self.fields_key = ["player_cpd_id", ]
                self.fields_value = ["player_cps_id", ]
                self.expected_values = [item.field_name for item in CCOMPARISON_MODELS[self.ccomp_type]]

            case CrossComparisonTypeConstant.POSITION_HERO:
                self.name = "Hero"
                self.fields_key = ["hero_cpd_id", ]
                self.fields_value = ["hero_cps_id", ]
                self.expected_values = [item.field_name for item in CCOMPARISON_MODELS[self.ccomp_type]]

            case CrossComparisonTypeConstant.POSITION_HERO_FACET:
                self.name = "Hero/Facet"
                self.fields_key = ["hero_cpd_id", 'facet_cpd_id', ]
                self.fields_value = ["hero_cps_id", 'facet_cps_id', ]
                self.expected_values = [item.field_name for item in CCOMPARISON_MODELS[self.ccomp_type]]
            case _:
                raise KeyError(f"No cross-comparison {self.ccomp_type} exists! (type {type(self.ccomp_type)})")

        self.replacement_values = { }
        self.ordered_header_map = set()


    def process_key(self, data_key: tuple) -> str:
        key_values = { name: value for value, name in zip(data_key, self.fields_key) }

        match self.ccomp_type:
            case None:
                team_cpd_id = key_values.pop("team_cpd_id")
                value = self.replacement_values.get(team_cpd_id, team_cpd_id)
            case CrossComparisonTypeConstant.POSITION_PLAYER:
                player_id = key_values.pop("player_cpd_id")
                value = self.replacement_values.get(player_id, player_id)
            case CrossComparisonTypeConstant.POSITION_HERO:
                # can be replaced here if we have a global dict
                value = key_values.pop("hero_cpd_id")
            case CrossComparisonTypeConstant.POSITION_HERO_FACET:
                # can be replaced here if we have a global dict
                hero = key_values.pop("hero_cpd_id")
                facet = key_values.pop("facet_cpd_id")
                value = f"{hero}/{facet}"
            case _:
                raise KeyError(f"No cross-comparison {self.ccomp_type} exists!")

        return value


    def _update_replacement_dict(self, data: dict) -> None:
        for k, v in self.REPLACEMENT_MAP.items():
            if k in data and v in data:
                replacement_key = data[k]
                replacement_value = data[v]
                if replacement_key not in self.replacement_values:
                    self.replacement_values[replacement_key] = replacement_value


    def process_data_row(self, *args) -> tuple:
        data = { name: value for value, name in zip(args, self.expected_values) }
        self._update_replacement_dict(data)
        print(data, args)
        dict_keys = tuple(data[x] for x in self.fields_key)
        dict_value_key = tuple(data[x] for x in self.fields_value)

        self.ordered_header_map.add(dict_keys)
        return dict_keys, dict_value_key


    def rearrange_dict(self, data: dict):
        ordered_headers = sorted(
            list(self.ordered_header_map),
            key=lambda x: self.process_key(x).lower()
        )
        output = list()
        ordered_formatted_header = []

        for outer_key in ordered_headers:
            row_data: dict = data.pop(outer_key)
            row_key = self.process_key(outer_key)
            ordered_formatted_header.append(row_key)
            row_output = { self.name: row_key }

            for inner_key in ordered_headers:
                value = row_data.get(inner_key, SENTINEL)

                if value is not SENTINEL:
                    key = self.process_key(inner_key)

                    if is_na_decimal(value):
                        value = None
                    self.TMMF.add(column=row_key, value=value)

                    row_output[key] = value
            output.append(row_output)
        return ordered_formatted_header, output
