from constants.league_and_patch_short_data import LeaguePatchShortDataConstant


class LeagueAndPatchShortDataMixin:
    """Mixin that contains dynamically created fields for "LeagueAndPatchShortDataMixin" class"""
    __mixin__ = True


class LeagueAndPatchShortDataMomentumMixin:
    """Mixin that contains dynamically created fields for "LeagueAndPatchShortDataMixin" class"""
    __mixin__ = True


for item in LeaguePatchShortDataConstant.VALUES:
    LeagueAndPatchShortDataMixin.__annotations__[item.name] = item.type_
    if item.is_comparable:
        LeagueAndPatchShortDataMomentumMixin.__annotations__[item.name] = item.type_
