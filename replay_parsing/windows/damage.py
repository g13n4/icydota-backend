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

