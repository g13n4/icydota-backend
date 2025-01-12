import copy
import re
from typing import ClassVar
from unicodedata import category

from pydantic import BaseModel

from constants.calculation.category import WindowCategories
from constants.helpers import GetItemHelper


##### POSTPORCESSING

PERCENTAGE_DATA = ['damage|from_all__dmg_inst', 'damage|from_all__median', 'damage|from_all__sum', 'damage|from_buildings__dmg_inst', 'damage|from_buildings__median', 'damage|from_buildings__sum', 'damage|from_creatures__dmg_inst', 'damage|from_creatures__median', 'damage|from_creatures__sum', 'damage|from_heroes__dmg_inst', 'damage|from_heroes__median', 'damage|from_heroes__sum', 'damage|from_illusions__dmg_inst', 'damage|from_illusions__median', 'damage|from_illusions__sum', 'damage|to_all__dmg_inst', 'damage|to_all__median', 'damage|to_all__sum', 'damage|to_buildings__dmg_inst', 'damage|to_buildings__median', 'damage|to_buildings__sum', 'damage|to_creatures__dmg_inst', 'damage|to_creatures__median', 'damage|to_creatures__sum', 'damage|to_heroes__dmg_inst', 'damage|to_heroes__median', 'damage|to_heroes__sum', 'damage|to_illusions__dmg_inst', 'damage|to_illusions__median', 'damage|to_illusions__sum', 'damage|with_summons__dmg_inst', 'damage|with_summons__median', 'damage|with_summons__sum', 'interval|deaths__avg_(by_length)_pm', 'interval|deaths__max', 'interval|deaths__max_global_perc', 'interval|gold__gained_pm_median', 'interval|gold__max_global_perc', 'interval|kda__avg_(by_length)_pm', 'interval|kda__max', 'interval|kills__avg_(by_length)_pm', 'interval|kills__max', 'interval|kills__max_global_perc', 'interval|lh__avg_(by_length)_pm', 'interval|lh__gained_pw', 'interval|movement__avg_(by_length)_pm', 'interval|movement__sum', 'interval|networth__gained_pw', 'interval|networth__max', 'interval|rune_pickups__max', 'interval|xp__gained_pm_median', 'interval|xp__max_global_perc', 'wards|was_dewarded_perc_obs', 'wards|was_dewarded_perc_sen']


# Compare data = slot 0: [1, 2, 3, 4, 3], slot 1: [1, 1, 2, 5, 3]
# for slot 0: [100%, 200%, 150%, 80%, 100%], for slot 1: [100%, 50%, 67%, 125%, 100%]
COMPARE_DATA_CORES = ['damage|from_all__dmg_inst', 'damage|from_all__median', 'damage|from_all__sum',
                      'damage|from_buildings__dmg_inst', 'damage|from_buildings__median', 'damage|from_buildings__sum',
                      'damage|from_creatures__dmg_inst', 'damage|from_creatures__median', 'damage|from_creatures__sum',
                      'damage|from_heroes__dmg_inst', 'damage|from_heroes__median', 'damage|from_heroes__sum',
                      'damage|from_illusions__dmg_inst', 'damage|from_illusions__median', 'damage|from_illusions__sum',
                      'damage|to_all__dmg_inst', 'damage|to_all__median', 'damage|to_all__sum',
                      'damage|to_buildings__dmg_inst', 'damage|to_buildings__median', 'damage|to_buildings__sum',
                      'damage|to_creatures__dmg_inst', 'damage|to_creatures__median', 'damage|to_creatures__sum',
                      'damage|to_heroes__dmg_inst', 'damage|to_heroes__median', 'damage|to_heroes__sum',
                      'damage|to_illusions__dmg_inst', 'damage|to_illusions__median', 'damage|to_illusions__sum',
                      'damage|with_summons__dmg_inst', 'damage|with_summons__median', 'damage|with_summons__sum',
                      'gold|death penalty', 'gold|gold for assist', 'gold|gold for killing buildings',
                      'gold|gold for killing creeps', 'gold|gold for killing heroes', 'gold|gold for killing neutrals',
                      'interval|deaths__avg_(by_length)_pm', 'interval|deaths__max', 'interval|deaths__max_global_perc',
                      'interval|gold__gained_pm_median', 'interval|gold__gained_pw', 'interval|gold__max',
                      'interval|gold__max_global_perc', 'interval|kda__avg_(by_length)_pm', 'interval|kda__max',
                      'interval|kills__avg_(by_length)_pm', 'interval|kills__max', 'interval|kills__max_global_perc',
                      'interval|level__max', 'interval|lh__avg_(by_length)_pm', 'interval|lh__gained_pw',
                      'interval|lh__max', 'interval|movement__avg_(by_length)_pm', 'interval|movement__sum',
                      'interval|networth__gained_pw', 'interval|networth__max', 'interval|rune_pickups__max',
                      'interval|teamfight_participation__avg', 'interval|xp__gained_pm_median',
                      'interval|xp__gained_pw', 'interval|xp__max', 'interval|xp__max_global_perc', 'xp|xp for creeps',
                      'xp|xp for creeps pm', 'xp|xp for heroes', 'xp|xp for heroes pm']


COMPARE_DATA_SUPPORT = ['damage|from_all__dmg_inst', 'damage|from_all__median', 'damage|from_all__sum',
                        'damage|from_buildings__dmg_inst', 'damage|from_buildings__median',
                        'damage|from_buildings__sum', 'damage|from_creatures__dmg_inst',
                        'damage|from_creatures__median', 'damage|from_creatures__sum', 'damage|from_heroes__dmg_inst',
                        'damage|from_heroes__median', 'damage|from_heroes__sum', 'damage|from_illusions__dmg_inst',
                        'damage|from_illusions__median', 'damage|from_illusions__sum', 'damage|to_all__dmg_inst',
                        'damage|to_all__median', 'damage|to_all__sum', 'damage|to_buildings__dmg_inst',
                        'damage|to_buildings__median', 'damage|to_buildings__sum', 'damage|to_creatures__dmg_inst',
                        'damage|to_creatures__median', 'damage|to_creatures__sum', 'damage|to_heroes__dmg_inst',
                        'damage|to_heroes__median', 'damage|to_heroes__sum', 'damage|to_illusions__dmg_inst',
                        'damage|to_illusions__median', 'damage|to_illusions__sum', 'damage|with_summons__dmg_inst',
                        'damage|with_summons__median', 'damage|with_summons__sum', 'gold|death penalty',
                        'gold|gold for assist', 'gold|gold for killing buildings', 'gold|gold for killing creeps',
                        'gold|gold for killing heroes', 'gold|gold for killing neutrals',
                        'interval|deaths__avg_(by_length)_pm', 'interval|deaths__max',
                        'interval|deaths__max_global_perc', 'interval|gold__gained_pm_median',
                        'interval|gold__gained_pw', 'interval|gold__max', 'interval|gold__max_global_perc',
                        'interval|kda__avg_(by_length)_pm', 'interval|kda__max', 'interval|kills__avg_(by_length)_pm',
                        'interval|kills__max', 'interval|kills__max_global_perc', 'interval|level__max',
                        'interval|lh__avg_(by_length)_pm', 'interval|lh__gained_pw', 'interval|lh__max',
                        'interval|movement__avg_(by_length)_pm', 'interval|movement__sum',
                        'interval|networth__gained_pw', 'interval|networth__max',
                        'interval|obs_placed__avg_(by_length)_pm', 'interval|obs_placed__max',
                        'interval|rune_pickups__max', 'interval|sen_placed__avg_(by_length)_pm',
                        'interval|sen_placed__max', 'interval|stacked__avg_(by_length)_pm', 'interval|stacked__max',
                        'interval|teamfight_participation__avg', 'interval|xp__gained_pm_median',
                        'interval|xp__gained_pw', 'interval|xp__max', 'interval|xp__max_global_perc',
                        'wards|killed_obs', 'wards|killed_obs_pm', 'wards|killed_sen', 'wards|killed_sen_pm',
                        'wards|was_dewarded_obs', 'wards|was_dewarded_perc_obs', 'wards|was_dewarded_perc_sen',
                        'wards|was_dewarded_sen', 'xp|xp for creeps', 'xp|xp for creeps pm', 'xp|xp for heroes',
                        'xp|xp for heroes pm']



# sum total = [1, 2, 3, 4, 3] => array + [1 + 2 + 3 + 4 +3]
MAX_TOTAL_DATA = ['interval|gold__max',
                  'interval|xp__max',
                  'interval|lh__max',
                  'interval|level__max',
                  'interval|kills__max', 'interval|deaths__max', 'interval|kda__max',
                  'interval|kda__avg_(by_length)_pm',
                  'interval|sen_placed__max', 'interval|stacked__max', 'interval|towers_killed__max',
                  'interval|roshans_killed__max', 'interval|networth__max', ]


SUM_TOTAL_DATA = ['damage|from_all__dmg_inst', 'damage|from_all__sum', 'damage|from_buildings__dmg_inst',
                  'damage|from_buildings__sum', 'damage|from_creatures__dmg_inst', 'damage|from_creatures__sum',
                  'damage|from_heroes__dmg_inst', 'damage|from_heroes__sum', 'damage|from_illusions__dmg_inst',
                  'damage|from_illusions__sum', 'damage|to_all__dmg_inst', 'damage|to_all__sum',
                  'damage|to_buildings__dmg_inst', 'damage|to_buildings__sum', 'damage|to_creatures__dmg_inst',
                  'damage|to_creatures__sum', 'damage|to_heroes__dmg_inst', 'damage|to_heroes__sum',
                  'damage|to_illusions__dmg_inst', 'damage|to_illusions__sum', 'damage|with_summons__dmg_inst',
                  'damage|with_summons__sum', 'gold|death penalty', 'gold|gold for assist',
                  'gold|gold for assisting killing couriers', "gold|gold for flag bearer (and doom's devour)",
                  'gold|gold for killing buildings', 'gold|gold for killing couriers', 'gold|gold for killing creeps',
                  'gold|gold for killing heroes', 'gold|gold for killing neutrals', 'gold|gold for killing roshan',
                  'gold|gold for wards', 'gold|gold runes', 'interval|movement__sum', 'interval|rune_pickups__max',
                  'wards|killed_obs', 'wards|killed_sen', 'wards|placed_wards_obs', 'wards|placed_wards_sen',
                  'wards|was_dewarded_obs', 'wards|was_dewarded_sen', 'xp|other', 'xp|xp for creeps',
                  'xp|xp for heroes', 'xp|xp for roshan', 'pings|pings']


# average total = [1, 2, 3, 4, 3] => array + [(1 + 2 + 3 + 4 +3) / 5]
AVERAGE_TOTAL_DATA = ['damage|from_all__mean', 'damage|from_all__median', 'damage|from_buildings__mean',
                      'damage|from_buildings__median', 'damage|from_creatures__mean', 'damage|from_creatures__median',
                      'damage|from_heroes__mean', 'damage|from_heroes__median', 'damage|from_illusions__mean',
                      'damage|from_illusions__median', 'damage|to_all__mean', 'damage|to_all__median',
                      'damage|to_buildings__mean', 'damage|to_buildings__median', 'damage|to_creatures__mean',
                      'damage|to_creatures__median', 'damage|to_heroes__mean', 'damage|to_heroes__median',
                      'damage|to_illusions__mean', 'damage|to_illusions__median', 'damage|with_summons__mean',
                      'damage|with_summons__median', 'gold|death penalty pm', 'gold|gold for assist pm',
                      'gold|gold for assisting killing couriers pm', "gold|gold for flag bearer (and doom's devour) pm",
                      'gold|gold for killing buildings pm', 'gold|gold for killing couriers pm',
                      'gold|gold for killing creeps pm', 'gold|gold for killing heroes pm',
                      'gold|gold for killing neutrals pm', 'gold|gold for killing roshan pm', 'gold|gold for wards pm',
                      'gold|gold runes pm', 'interval|deaths__avg_(by_length)_pm', 'interval|deaths__max_global_perc',
                      'interval|gold__avg_(by_length)_pm', 'interval|gold__gained_pm_median',
                      'interval|gold__gained_pw', 'interval|gold__max_global_perc', 'interval|kda__gained_pw',
                      'interval|kills__avg_(by_length)_pm', 'interval|kills__max_global_perc',
                      'interval|level__gained_pw', 'interval|lh__avg_(by_length)_pm', 'interval|lh__gained_pw',
                      'interval|movement__avg_(by_length)_pm', 'interval|networth__gained_pw',
                      'interval|obs_placed__avg_(by_length)_pm', 'interval|obs_placed__max',
                      'interval|sen_placed__avg_(by_length)_pm', 'interval|stacked__avg_(by_length)_pm',
                      'interval|teamfight_participation__avg', 'interval|teamfight_participation__max',
                      'interval|teamfight_participation__min', 'interval|towers_killed__gained_pw',
                      'interval|xp__avg_(by_length)_pm', 'interval|xp__gained_pm_median', 'interval|xp__gained_pw',
                      'interval|xp__max_global_perc', 'pings|pings_per_minute', 'wards|killed_obs_pm',
                      'wards|killed_sen_pm', 'wards|was_dewarded_perc_obs', 'wards|was_dewarded_perc_sen',
                      'xp|xp for creeps pm', 'xp|xp for heroes pm']


class PostprocessingItem(BaseModel):
    carry_comparison: bool = False
    support_comparison: bool = False

    percentage: bool = False

    max_total: bool = False
    sum_total: bool = False
    average_total: bool = False


def check_name(name) -> str | None:
    default = dict()

    if name in PERCENTAGE_DATA:
        default['percentage'] = True

    if name in COMPARE_DATA_CORES:
        default['carry_comparison'] = True

    if name in COMPARE_DATA_SUPPORT:
        default['support_comparison'] = True

    if name in MAX_TOTAL_DATA:
        default['max_total'] = True

    if name in SUM_TOTAL_DATA:
        default['sum_total'] = True

    if name in AVERAGE_TOTAL_DATA:
        default['average_total'] = True

    return f'{PostprocessingItem(**default)=}' if default else None

# VALUES
INTERVAL_WINDOWS = {
    'Gold': ('gold', 'max'),  # gold at the end of the window
    'Gold median (per minute)': ('gold', 'gained_pm_median'),  # gold per minute (median value)
    'Gold gained': ('gold', 'gained_pw'),  # gold gained per window
    'GPM': ('gold', 'avg_(by_length)_pm'),  # gpm (window gain by length)
    'Gold control (total%)': ('gold', 'max_global_perc'),  # what percent of total gold hero controls

    'XP': ('xp', 'max'),
    'XP median (per minute)': ('xp', 'gained_pm_median'),
    'XP gained': ('xp', 'gained_pw'),
    'XPM': ('xp', 'avg_(by_length)_pm'),
    'XP control (total%)': ('xp', 'max_global_perc'),

    'Last hits': ('lh', 'max'),
    'Last hits gained': ('lh', 'gained_pw'),
    'Last hits average (per minute)': ('lh', 'avg_(by_length)_pm'),

    'Distance traveled': ('movement', 'sum'),
    'Distance traveled (per minute)': ('movement', 'avg_(by_length)_pm'),

    'Level': ('level', 'max'),
    'Levels gained': ('level', 'gained_pw'),

    'Kills': ('kills', 'max'),
    'Kills average (per minute)': ('kills', 'avg_(by_length)_pm'),
    'Kills control (total%)': ('kills', 'max_global_perc'),

    'Deaths': ('deaths', 'max'),
    'Deaths average (per minute)': ('deaths', 'avg_(by_length)_pm'),
    'Deaths control (total%)': ('deaths', 'max_global_perc'),

    'KDA': ('kda', 'max'),
    'KDA average (per minute)': ('kda', 'avg_(by_length)_pm'),
    'KDA gained': ('kda', 'gained_pw'),

    'Observer wards placed': ('obs_placed', 'max'),
    'Observer wards placed (per minute)': ('obs_placed', 'avg_(by_length)_pm'),

    'Sentry wards placed': ('sen_placed', 'max'),
    'Sentry wards placed (per minute)': ('sen_placed', 'avg_(by_length)_pm'),

    'Stacked': ('stacked', 'max'),
    'Stacked average (per minute)': ('stacked', 'avg_(by_length)_pm'),

    'Runes picked up': ('rune_pickups', 'max'),

    'Team fight participation average': ('teamfight_participation', 'avg'),
    'Team fight participation max': ('teamfight_participation', 'max'),
    'Team fight participation min': ('teamfight_participation', 'min'),

    'Towers kills': ('towers_killed', 'max'),
    'Towers kills gained (per minute)': ('towers_killed', 'gained_pw'),

    'Roshan kills': ('roshans_killed', 'max'),

    'Networth': ('networth', 'max'),
    'Networth gained': ('networth', 'gained_pw'),
}

PINGS_WINDOWS = {
    'Pings': 'pings',
    'Pings (per minute)': 'pings_per_minute',
}



DAMAGE_WINDOWS = {
    f'{name_agg} {name_type}': f'{column_agg}__{agg_type}' for name_agg, column_agg in [
        ('With summons', 'with_summons'),
        ('To heroes', 'to_heroes'),
        ('To buildings', 'to_buildings'),
        ('To npcs', 'to_creatures'),
        ('To illusions', 'to_illusions'),
        ('Dealt to all', 'to_all'),
        ('From heroes', 'from_heroes'),
        ('From buildings', 'from_buildings'),
        ('From npcs', 'from_creatures'),
        ('From illusions', 'from_illusions'),
        ('Received from all', 'from_all'),
    ]
    for name_type, agg_type in [
        ('(total)', 'sum'),
        ('(mean)', 'mean'),
        ('(median)', 'median'),
        ('(number of instances)', 'dmg_inst'),
    ]
}



WARDS_WINDOWS = {
    'Placed sentries': 'placed_wards_sen',
    'Placed observers': 'placed_wards_obs',
}

DEWARD_WINDOWS = {
    'Number of dewarded sentries': 'was_dewarded_sen',
    'Number of dewarded observers': 'was_dewarded_obs',
    'Percent of dewarded sentries': 'was_dewarded_perc_sen',
    'Percent of dewarded observers': 'was_dewarded_perc_obs',
    'Sentry kills': 'killed_sen',
    'Observer kills': 'killed_obs',
    'Sentry kills (per minute)': 'killed_sen_pm',
    'Observer kills (per minute)': 'killed_obs_pm',
}



XP_WINDOWS = {
    'Other XP': 'other',
    'XP for heroes': 'xp for heroes',
    'XP for heroes (per minute)': 'xp for heroes pm',
    'XP for creeps': 'xp for creeps',
    'XP for creeps (per minute)': 'xp for creeps pm',
    'XP for roshan': 'xp for roshan',
}


GOLD_WINDOWS = {
    'Gold removed for death': 'death penalty',
    'Gold removed for death (per minute)': 'death penalty pm',
    'Gold for assists': 'gold for assist',
    'Gold for assists (per minute)': 'gold for assist pm',
    'Gold for killing buildings': 'gold for killing buildings',
    'Gold for killing buildings (per minute)': 'gold for killing buildings pm',
    'Gold for killing heroes': 'gold for killing heroes',
    'Gold for killing heroes (per minute)': 'gold for killing heroes pm',
    'Gold for killing creeps': 'gold for killing creeps',
    'Gold for killing creeps (per minute)': 'gold for killing creeps pm',
    'Gold for killing neutrals': 'gold for killing neutrals',
    'Gold for killing neutrals (per minute)': 'gold for killing neutrals pm',
    'Gold for killing roshan': 'gold for killing roshan',
    'Gold for killing roshan (per minute)': 'gold for killing roshan pm',
    'Gold for courier assists': 'gold for assisting killing couriers',
    'Gold for courier assists (per minute)': 'gold for assisting killing couriers pm',
    'Gold for runes': 'gold runes',
    'Gold for runes (per minute)': 'gold runes pm',
    'Gold for flag bearers, devour, etc': 'gold for flag bearer (and doom\'s devour)',
    'Gold for flag bearers, devour, etc (per minute)': 'gold for flag bearer (and doom\'s devour) pm',
    'Gold for wards': 'gold for wards',
    'Gold for wards (per minute)': 'gold for wards pm',
    'Gold for couriers': 'gold for killing couriers',
    'Gold for couriers (per minute)': 'gold for killing couriers pm',
}



ALL_WINDOWS = {
    'interval': INTERVAL_WINDOWS,
    'pings': PINGS_WINDOWS,
    'damage': DAMAGE_WINDOWS,
    'wards': WARDS_WINDOWS,
    'deward': DEWARD_WINDOWS,
    'xp': XP_WINDOWS,
    'gold': GOLD_WINDOWS,
}

intk = set()
intv = set()

category_dict = {
    item.value: f'WindowCategories.{item.name}' for item in WindowCategories.VALUES
}

data_template = {
    'name': None,
    'description': None,
    'value': None,
    'index': None,
    'category': None,
    'postprocessing': None,
    'aggregation': None,
}

def print_data(data):
    print(f'{data["name"]}: CalculationItem = CalculationItem(')
    for k, v in data.items():
        if v is not None:
            if k in ['description', 'name']:
                print(f'{k} = "{v}",')
            else:
                print(f'{k} = {v},')
    print(')')

def remove_(text: str) -> str:
    return text.replace('(', '').replace(')', '').replace('\'', '')


counter = 0
for category_idx, window  in enumerate(ALL_WINDOWS.items(), 1):
    window_name, v = window
    print(window_name)

    for idx, values in enumerate(v.items(), 1):
        data = copy.deepcopy(data_template)
        description, name = values
        counter += 1

        data['description'] = description
        data['index'] = idx
        data['value'] = counter


        if type(name) is tuple:
            intk.add(name[0].upper())
            intv.add(name[1].upper())

            data['calculation'] = f'(IntervalCalculationCategory.{name[0].upper()}, IntervalCalculationType.{remove_(name[1].upper())})'

            proper_name = '__'.join(name)
            data['name'] = remove_(proper_name)

            old_name = '|'.join((window_name, proper_name))

            data['postprocessing'] = check_name(old_name)

        else:
            old_name = '|'.join((window_name, name))

            if re.search(r"\s", name):
                name = '_'.join(name.split(" ")).lower()

            data['name'] = remove_(name)
            data['postprocessing'] = check_name(old_name)

        # data['category'] = category_dict[category_idx]
        print_data(data)
    print('\n')

print(intk)
print(intv)

