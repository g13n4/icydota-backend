DAMAGE_WINDOWS = {
    f'{name_agg} {name_type}': f'{column_agg}__{agg_type}' for name_agg, column_agg in [
        ('Damage dealt with summons', 'with_summons'),
        ('Damage dealt to heroes', 'to_heroes'),
        ('Damage dealt to buildings', 'to_buildings'),
        ('Damage dealt to npcs', 'to_creatures'),
        ('Damage dealt to illusions', 'to_illusions'),
        ('Damage dealt', 'to_all'),
        ('Damage received from heroes', 'from_heroes'),
        ('Damage received from buildings', 'from_buildings'),
        ('Damage received from npcs', 'from_creatures'),
        ('Damage received from illusions', 'from_illusions'),
        ('Damage received', 'from_all'),
    ]
    for name_type, agg_type in [
        ('(total)', 'sum'),
        ('(mean)', 'mean'),
        ('(median)', 'median'),
        ('(number of instances)', 'dmg_inst'),
    ]
}

DAMAGE_WINDOWS_AGGS = DAMAGE_WINDOWS.values()
