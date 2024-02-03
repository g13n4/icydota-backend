from typing import Dict, Any

from replay_parsing import ODOTAPositionNormaliser


def fix_odota_data(odota_data: Dict[str, Any]) -> None:
    # TEST
    slots_are_broken = False
    position_tester = {
        'dire': set(),
        'radiant': set(),
    }
    position_data = {
        'dire': [],
        'radiant': [],
    }

    for player in odota_data['players']:
        this_player_slot = player['player_slot']
        if not (0 <= this_player_slot < 10):
            slots_are_broken = True

        side = 'radiant' if player['isRadiant'] else 'dire'

        position_tester[side].add(player['lane_role'])  # KeyError: 'lane_role' 7248385188
        position_data[side].append({
            'hero_id': player['hero_id'],
            'neutral_kills': player['neutral_kills'],
            'lane_role': player['lane_role'], })

    # SLOTS
    if slots_are_broken:
        for player in odota_data['players']:
            offset = 0 if player['isRadiant'] else 5
            player['player_slot'] = player['team_slot'] + offset

        #
        # for choice in odota_data['draft_timings']:
        #     if choice['pick']:
        #         real_slots[choice['hero_id']]: int = choice['player_slot']
        #
        # assert all([(x in real_slots.values()) for x in range(10)])
        #
        # for player in odota_data['players']:
        #     this_player_hero = player['hero_id']
        #     player['player_slot'] = real_slots[this_player_hero]

    # POSITIONS
    for isRadiant, side in enumerate(['dire', 'radiant']):
        if len(position_tester[side]) < 5:
            normalised_positions = ODOTAPositionNormaliser(position_data[side]).get_hero_to_positions()
            for player in odota_data['players']:
                hero_id = player['hero_id']
                if hero_id in normalised_positions:
                    player['lane_role'] = normalised_positions[hero_id]

    return None
