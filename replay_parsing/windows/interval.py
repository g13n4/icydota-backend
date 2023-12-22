# True - calculations are made with values accumulated up until this window
# False - calculations are made only with values from this window
# For example: There was a kill in a previous window l2.
# If it's True - number of kills we have is 1 even though we are in window l4
# If it's False - number of kills is zero because there were no kills in window l4

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

INTERVAL_WINDOWS_AGGS = INTERVAL_WINDOWS.values()
