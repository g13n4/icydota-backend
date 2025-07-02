import enum


class CaseInsensitiveEnum(str, enum.Enum):
    @classmethod
    def _missing_(cls, value: str):
        for member in cls:
            if member.lower() == value.lower():
                return member
        return None


class ProcessTypes(CaseInsensitiveEnum):
    match = "match"
    aggregation = "aggregation"
    cross_comparison = "cross_comparison"


class CrossComparisonPositionEnum(CaseInsensitiveEnum):
    support = "support"
    core = "core"
    mid = "mid"


class GameStageEnum(CaseInsensitiveEnum):
    lane = "lane"
    game = "game"
    both = "both"


    @classmethod
    def __missing__(cls, value):
        for member in cls:
            if member.lower() == value.lower():
                return member
        return cls.both


class FieldTypesEnum(CaseInsensitiveEnum):
    window = "window"
    total = "total"


class ComparisonTypeEnum(CaseInsensitiveEnum):
    player = "player"
    basic = "basic"
    general = "general"


    def to_value(self) -> bool:
        if self == self.player or self == self.basic:
            return False
        elif self == self.general:
            return True

        raise ValueError("Can only be used if Enum is value")


class ComparisonEnum(CaseInsensitiveEnum):
    flat = "flat"
    perc = "perc"
    none = "none"


    def to_value(self) -> bool | None:
        if self == self.flat:
            return True
        elif self == self.perc:
            return False
        elif self == self.none:
            return None

        raise ValueError("Can only be used if Enum is value")


class PoTEnum(CaseInsensitiveEnum):
    player = "player"
    team = "team"


    def isPlayer(self):
        return self == PoTEnum.player


class LoPEnum(CaseInsensitiveEnum):
    league = "league"
    patch = "patch"


    def to_api(self, value: int) -> tuple[int | None, int | None]:
        if self == LoPEnum.league:
            return value, None
        else:
            return None, value
