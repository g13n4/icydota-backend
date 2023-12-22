LANE_COLUMNS = ['l2', 'l4', 'l6', 'l8', 'l10', ]
GAME_COLUMNS = ['g15', 'g30', 'g45', 'g60', 'g60plus']

# Percentage data = [1, 2, 3, 4, 3] => [100%, 200%, 150%, 133%, 75%]
PERCENTAGE_DATA = ['damage|from_all__dmg_inst', 'damage|from_all__median', 'damage|from_all__sum', 'damage|from_buildings__dmg_inst', 'damage|from_buildings__median', 'damage|from_buildings__sum', 'damage|from_creatures__dmg_inst', 'damage|from_creatures__median', 'damage|from_creatures__sum', 'damage|from_heroes__dmg_inst', 'damage|from_heroes__median', 'damage|from_heroes__sum', 'damage|from_illusions__dmg_inst', 'damage|from_illusions__median', 'damage|from_illusions__sum', 'damage|to_all__dmg_inst', 'damage|to_all__median', 'damage|to_all__sum', 'damage|to_buildings__dmg_inst', 'damage|to_buildings__median', 'damage|to_buildings__sum', 'damage|to_creatures__dmg_inst', 'damage|to_creatures__median', 'damage|to_creatures__sum', 'damage|to_heroes__dmg_inst', 'damage|to_heroes__median', 'damage|to_heroes__sum', 'damage|to_illusions__dmg_inst', 'damage|to_illusions__median', 'damage|to_illusions__sum', 'damage|with_summons__dmg_inst', 'damage|with_summons__median', 'damage|with_summons__sum', 'interval|deaths__avg_(by_length)_pm', 'interval|deaths__max', 'interval|deaths__max_global_perc', 'interval|gold__gained_pm_median', 'interval|gold__max_global_perc', 'interval|kda__avg_(by_length)_pm', 'interval|kda__max', 'interval|kills__avg_(by_length)_pm', 'interval|kills__max', 'interval|kills__max_global_perc', 'interval|lh__avg_(by_length)_pm', 'interval|lh__gained_pw', 'interval|movement__avg_(by_length)_pm', 'interval|movement__sum', 'interval|networth__gained_pw', 'interval|networth__max', 'interval|rune_pickups__max', 'interval|xp__gained_pm_median', 'interval|xp__max_global_perc', 'wards|was_dewarded_perc_obs', 'wards|was_dewarded_perc_sen']


# Compare data = slot 0: [1, 2, 3, 4, 3], slot 1: [1, 1, 2, 5, 3]
# for slot 0: [100%, 200%, 150%, 80%, 100%], for slot 1: [100%, 50%, 67%, 125%, 100%]
COMPARE_DATA = ['damage|from_all__dmg_inst', 'damage|from_all__median', 'damage|from_all__sum', 'damage|from_buildings__dmg_inst', 'damage|from_buildings__median', 'damage|from_buildings__sum', 'damage|from_creatures__dmg_inst', 'damage|from_creatures__median', 'damage|from_creatures__sum', 'damage|from_heroes__dmg_inst', 'damage|from_heroes__median', 'damage|from_heroes__sum', 'damage|from_illusions__dmg_inst', 'damage|from_illusions__median', 'damage|from_illusions__sum', 'damage|to_all__dmg_inst', 'damage|to_all__median', 'damage|to_all__sum', 'damage|to_buildings__dmg_inst', 'damage|to_buildings__median', 'damage|to_buildings__sum', 'damage|to_creatures__dmg_inst', 'damage|to_creatures__median', 'damage|to_creatures__sum', 'damage|to_heroes__dmg_inst', 'damage|to_heroes__median', 'damage|to_heroes__sum', 'damage|to_illusions__dmg_inst', 'damage|to_illusions__median', 'damage|to_illusions__sum', 'damage|with_summons__dmg_inst', 'damage|with_summons__median', 'damage|with_summons__sum', 'gold|death penalty', 'gold|gold for assist', 'gold|gold for killing buildings', 'gold|gold for killing creeps', 'gold|gold for killing heroes', 'gold|gold for killing neutrals', 'interval|deaths__avg_(by_length)_pm', 'interval|deaths__max', 'interval|deaths__max_global_perc', 'interval|gold__gained_pm_median', 'interval|gold__gained_pw', 'interval|gold__max', 'interval|gold__max_global_perc', 'interval|kda__avg_(by_length)_pm', 'interval|kda__max', 'interval|kills__avg_(by_length)_pm', 'interval|kills__max', 'interval|kills__max_global_perc', 'interval|level__max', 'interval|lh__avg_(by_length)_pm', 'interval|lh__gained_pw', 'interval|lh__max', 'interval|movement__avg_(by_length)_pm', 'interval|movement__sum', 'interval|networth__gained_pw', 'interval|networth__max', 'interval|rune_pickups__max', 'interval|teamfight_participation__avg', 'interval|xp__gained_pm_median', 'interval|xp__gained_pw', 'interval|xp__max', 'interval|xp__max_global_perc', 'xp|xp for creeps', 'xp|xp for creeps pm', 'xp|xp for heroes', 'xp|xp for heroes pm']


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
                  'xp|xp for heroes', 'xp|xp for roshan']

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

ALL_DATA_TO_COMPARE = {
    'carry': COMPARE_DATA,
    'support': COMPARE_DATA_SUPPORT,
}
