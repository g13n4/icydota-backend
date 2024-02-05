import os
import pathlib

from replay_parsing import MatchAnalyser, MatchSplitter, process_interval_windows, \
    process_pings_windows, process_wards_windows, process_deward_windows, process_damage_windows, \
    process_xp_windows, process_gold_windows, process_building, postprocess_data, \
    process_hero_deaths, process_roshan_deaths


print(os.getcwd())

def _combine_dicts(*args) -> dict:
    data = {f'_{x}': {} for x in range(10)}
    for x in range(10):
        for item in args:
            key = f'_{x}'
            data[key].update(item[key])
    return data


def get_replay_info(path):
    match = MatchAnalyser(pathlib.Path(path))
    match_data = match.get_match_data()
    match.players.set_position_from_list([1, 4, 5, 2, 3, 1, 2, 3, 4, 5])
    match.players.set_player_data_from_dict({
        x: {
            'hero_id': 100,
            'player_id': 100,
        } for x in range(10)
    })

    MS = MatchSplitter(game_length=match.game_length, match_windows=match.match_windows)

    interval = process_interval_windows(match_data['interval'], MS, )
    pings = process_pings_windows(match_data['pings'], MS)

    wards = process_wards_windows(match_data['wards'], MS, )
    deward = process_deward_windows(match_data['deward'], MS,
                                    players=match.get_players(),
                                    players_to_slot=match.players.get_name_slot_dict())

    damage = process_damage_windows(match_data['damage'], MS, players=match.get_players())
    xp = process_xp_windows(match_data['xp'], MS, players_to_slot=match.players.get_name_slot_dict())
    gold = process_gold_windows(match_data['gold'], MS, players_to_slot=match.players.get_name_slot_dict())

    match_info = _combine_dicts(interval, pings, wards, deward, damage, xp, gold)

    set_totals, comparison_data = postprocess_data(match_info, match.get_players_object(), MS)

    # additional info
    player_hero_info, ftk_dire, hero_deaths = process_hero_deaths(match_data['hero_deaths'],
                                                                  players_to_slot=match.players.get_name_slot_dict())

    roshan_deaths = process_roshan_deaths(match_data['roshan_deaths'],
                                          players_to_slot=match.players.get_name_slot_dict())

    player_building_info, building_kill = process_building(match_data['building_kill'],
                                                           pos_to_slot=match.players.get_pos_to_slot_by_side())

    return comparison_data


if __name__ == '__main__':
    get_replay_info('replays/7559306183/7559306183.jsonl')
