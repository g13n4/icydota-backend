from replay_parsing import MatchAnalyser, MatchSplitter, process_interval_windows, \
    process_pings_windows, process_wards_windows, process_deward_windows, process_damage_windows, \
    process_xp_windows, process_gold_windows, process_building_windows
import pathlib
import os



print(os.getcwd())

def main(path):
    match = MatchAnalyser(pathlib.Path(path))
    match_data = match.get_match_data()

    MS = MatchSplitter(game_length=match.get_game_length())

    interval = process_interval_windows(match_data['interval'], MS)
    pings = process_pings_windows(match_data['pings'], MS)

    wards = process_wards_windows(match_data['wards'], MS, )
    deward = process_deward_windows(match_data['deward'], MS,
                                    players=match.get_players(),
                                    players_to_slot=match.players.get_name_slot_dict())

    damage = process_damage_windows(match_data['damage'], MS, players=match.get_players())
    xp = process_xp_windows(match_data['xp'], MS, players_to_slot=match.players.get_name_slot_dict())
    gold = process_gold_windows(match_data['gold'], MS, players_to_slot=match.players.get_name_slot_dict())
    building_kill = process_building_windows(match_data['building_kill'])

    print(building_kill)


main('replays/7393133836/7393133836.jsonl')


