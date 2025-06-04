import enum

from utils import CaseInsensitiveEnum


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
    general = "general"

    def to_value(self) -> bool:
        if self == self.player:
            return False
        elif self == self.general:
            return True

        raise ValueError("Can only be used if Enum is value")


class ComparisonEnum(CaseInsensitiveEnum):
    flat = "flat"
    perc = "perc"
    none = "none"

    def to_value(self)  -> bool | None:
        if self == self.flat:
            return True
        elif self == self.perc:
            return False
        elif self == self.none:
            return None

        raise ValueError("Can only be used if Enum is value")


class PoTEnum(CaseInsensitiveEnum):
    PLAYER = "PLAYER"
    TEAM = "TEAM"

    def isPlayer(self):
        return self == PoTEnum.PLAYER


class LoPEnum(CaseInsensitiveEnum):
    LEAGUE = "LEAGUE"
    PATCH = "PATCH"

    def to_api(self, value: int) -> tuple[int | None, int | None]:
        if self == LoPEnum.LEAGUE:
            return value, None
        else:
            return None, value

