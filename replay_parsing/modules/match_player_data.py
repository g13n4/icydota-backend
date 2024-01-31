from typing import Dict, List, Any

from utils import get_both_slot_values
from ..ingame_data import POSITION_NAMES, POSITION_OPPONENTS


class MatchPlayersData:
    def __init__(self):
        for x in range(10):
            setattr(self, f'_{x}', {
                'slot': x,
                'slot_text': f'_{x}',
                'side': 'sentinel' if x < 5 else 'dire',

                'hero_npc_name': None,
                'hero_npc_name_alias': None,
                'hero_name_cdota': None,
                'hero_id': None,

                'position': None,
                'position_id': None,
                'position_name': None,

                'player': None,
                'player_id': None,

                'opponents': [],

            })

    def update_slot_info(self, slot: int, **kwargs) -> None:
        info = getattr(self, f'_{slot}')
        setattr(self, f'_{slot}', {**info, **kwargs})

    def update_slot_name(self, slot: int, name: str) -> None:
        info = getattr(self, f'_{slot}')
        if not info['hero_npc_name']:
            info['hero_npc_name'] = name
        elif not info['hero_npc_name_alias']:
            info['hero_npc_name_alias'] = name
        else:
            raise ValueError('Hero has too many names!')

        setattr(self, f'_{slot}', info)

    def get_pos_to_slot_by_side(self) -> Dict[str, Dict[int, int]]:
        all_players = self.get_all()
        data = {
            'sentinel': dict(),
            'dire': dict(),
        }
        for player in all_players:
            data[player['side']][player['position']] = player['slot']

        return data

    def get_name_slot_dict(self) -> Dict[str, int]:
        items = self.get_all()
        names = {x['hero_npc_name']: x['slot'] for x in items}
        alias = {x['hero_npc_name_alias']: x['slot'] for x in items if x['hero_npc_name_alias']}
        return {**names, **alias}

    def get_all(self) -> List[Dict[str, Any]]:
        return [getattr(self, f'_{x}') for x in range(10)]

    def get_dire(self) -> list:
        return [getattr(self, f'_{x}') for x in range(10) if x >= 5]

    def _get_by_name(self, key_name: str, value_name: str) -> dict:
        for item in self.get_all():
            if item[key_name] == value_name:
                return item
        raise KeyError

    def get_by_cdata_name(self, name: str) -> dict:
        return self._get_by_name('name_cdata', name)

    def get_by_ingame_name(self, name: str) -> dict:
        return self._get_by_name('name_ingame', name)

    def __repr__(self):
        return '\n'.join([str(x) for x in self.get_all()])

    def __getitem__(self, slot: int) -> Dict[str, Any]:
        if 0 <= slot < 10:
            return getattr(self, f'_{slot}')
        else:
            raise KeyError(f"No slot {slot}! Only ten players are in the game")

    def set_position_from_dict(self, positions: Dict[str | int, int]):
        """
        :param positions: dictionary where key is the slot of the player and key is his position
        """
        for k, v in positions.items():
            slot_text, slot = get_both_slot_values(k)
            player = getattr(self, slot_text)
            player['position'] = v
            player['position_name'] = POSITION_NAMES[v]
        self._set_opponents()

    def _new_data_check(self):
        test_player = getattr(self, '_0')
        if test_player['position']:
            self._set_position_names()
            self._set_opponents()

    def set_player_data_from_dict(self, players_info: Dict[int, Dict[str, Any]]):
        players = self.get_all()
        for player in players:
            player.update(players_info[player['slot']])
        self._new_data_check()

    def _set_position_names(self):
        players = self.get_all()
        for player in players:
            player['position_name'] = POSITION_NAMES[player['position']]
        return

    def set_position_from_list(self, opponents: List[int]):
        players = self.get_all()
        for player, pos in zip(players, opponents):
            player['position'] = pos
            player['position_name'] = POSITION_NAMES[pos]
        self._set_opponents()

    def _set_opponents(self):
        players = self.get_all()
        for player in players:
            player_position = player['position']
            player_opponents_positions = POSITION_OPPONENTS[player_position]

            for opponent in players:
                if player['side'] == opponent['side'] and not (opponent['position'] in player_opponents_positions):
                    continue

                player['opponents'].append(opponent['slot'])
