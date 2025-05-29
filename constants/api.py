import enum

from utils import CaseInsensitiveEnum


class CrossComparisonPositionEnum(CaseInsensitiveEnum):
    SUPPORT = "support"
    CORE = "core"
    MID = "mid"


class GameStageEnum(CaseInsensitiveEnum):
    LANE = "lane"
    GAME = "game"
    BOTH = "both"


    @classmethod
    def __missing__(cls, value):
        for member in cls:
            if member.lower() == value.lower():
                return member
        return cls.BOTH


class FieldTypesEnum(CaseInsensitiveEnum):
    WINDOW = "window"
    TOTAL = "total"


class ComparisonTypeEnum(CaseInsensitiveEnum):
    PLAYER = False
    GENERAL = True


class ComparisonEnum(enum.Enum):
    FLAT = True
    PERC = False
    NONE = None


class PoTEnum(CaseInsensitiveEnum):
    PLAYER = "player"
    TEAM = "team"

    def isPlayer(self):
        return self == PoTEnum.PLAYER


class LoPEnum(CaseInsensitiveEnum):
    LEAGUE = "league"
    PATCH = "patch"

    def to_api(self, value: int) -> tuple[int | None, int | None]:
        if self == LoPEnum.LEAGUE:
            return value, None
        else:
            return None, value

