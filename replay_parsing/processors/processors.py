import pandas as pd
import copy


def process_df(df: pd.DataFrame, players: list) -> dict:
    player_stats_dfs = {
        'to_all': None,
        'with_summons': None,
        'to_heroes': None,
        'to_buildings': None,
        'to_creatures': None,
        'to_illusions': None,

        'from_all': None,
        'from_heroes': None,
        'from_buildings': None,
        'from_creatures': None,
        'from_illusions': None,

    }
    response = dict()

    required_columns = ['time', 'value']

    df['frombuilding'] = df['sourcename'].str.contains('_tower|_rax_|_fillers|fort', regex=True)
    df['tobuilding'] = df['targetname'].str.contains('_tower|_rax_|_fillers|fort', regex=True)

    for player in players:
        response[f'_{player["slot"]}'] = copy.deepcopy(player_stats_dfs)
        player_info = response[f'_{player["slot"]}']
        name_match = player['hero_npc_name'] + ('|' + player['hero_npc_name'] if player['hero_npc_name'] else '')

        player_attack = df[df['sourcename'].str.contains(name_match, regex=True)]

        player_info['with_summons'] = player_attack[player_attack.attackerhero != True][required_columns]
        player_info['to_heroes'] = player_attack[player_attack.targethero == True][required_columns]
        player_info['to_buildings'] = player_attack[player_attack.tobuilding == True][required_columns]
        player_info['to_creatures'] = player_attack[((player_attack.tobuilding == False) &
                                                     (player_attack.targethero == False) &
                                                     (player_attack.targetillusion == False))][required_columns]
        player_info['to_illusions'] = player_attack[player_attack.targetillusion == True][required_columns]

        player_info['to_all'] = player_attack[required_columns]

        player_defense = df[df['targetsourcename'].str.contains(name_match, regex=True)]

        player_info['from_heroes'] = player_defense[player_defense.attackerhero.istr][required_columns]
        player_info['from_buildings'] = player_defense[player_defense.frombuilding == True][required_columns]
        player_info['from_creatures'] = player_defense[((player_defense.frombuilding == False) &
                                                        (player_defense.attackerhero == False) &
                                                        (player_defense.attackerillusion == False))][required_columns]
        player_info['from_illusions'] = player_defense[player_defense.attackerillusion == True][required_columns]
        player_info['from_all'] = player_defense[required_columns]

    return response
