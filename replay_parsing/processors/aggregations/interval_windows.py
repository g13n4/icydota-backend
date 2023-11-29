# True - calculations are made with values accumulated up until this window
# False - calculations are made only with values from this window
# For example: There was a kill in a previous window l2.
# If it's True - number of kills we have is 1 even though we are in window l4
# If it's False - number of kills is zero because there was no kills in window l4

INTERVAL_WINDOWS = [
    ('gold', 'max'),  # gold at the end of the window
    ('gold', 'gained_pm_median'),  # gold per minute (median value)
    ('gold', 'gained_pw'),  # gold gained per window
    ('gold', 'avg_(by_length)'),  # gpm (window gain by length)
    ('gold', 'max_global_perc'),  # what percent of total gold hero controls

    ('xp', 'max'),
    ('xp', 'gained_pm_median'),
    ('xp', 'gained_pw'),
    ('xp', 'avg_(by_length)'),
    ('xp', 'max_global_perc'),

    ('lh', 'max'),
    ('lh', 'gained_pw'),
    ('lh', 'avg_(by_length)'),

    ('movement', 'sum'),
    ('movement', 'avg_(by_length)'),

    ('level', 'max'),
    ('level', 'gained_pw'),

    ('kills', 'max'),
    ('kills', 'avg_(by_length)'),
    ('kills', 'max_global_perc'),

    ('deaths', 'max'),
    ('deaths', 'avg_(by_length)'),
    ('deaths', 'max_global_perc'),

    ('kda', 'max'),
    ('kda', 'gained_pw'),

    ('obs_placed', 'max'),
    ('obs_placed', 'avg_(by_length)'),

    ('sen_placed', 'max'),
    ('sen_placed', 'avg_(by_length)'),

    ('stacked', 'max'),
    ('stacked', 'avg_(by_length)'),

    ('rune_pickups', 'max'),

    ('teamfight_participation', 'avg'),
    ('teamfight_participation', 'max'),
    ('teamfight_participation', 'min'),

    ('towers_killed', 'max'),
    ('towers_killed', 'gained_pw'),

    ('roshans_killed', 'max'),

    ('networth', 'max'),
    ('networth', 'gained_pw'),
]
