import copy
from typing import Dict, List, Any


default_player_data_dict = {
    'hero_id': None,
    'neutral_kills': None,
    'lane_role': None, }


def _move_two_to_the_end(item: int) -> int:
    if item == 2:
        return 100
    return item


class ODOTAPositionNormaliser:
    def __init__(self, odota_players_data: List[Dict[str, Any]]):
        self.positions = {
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
        }

        self._move_priority = {
            1: 5,
            2: None,
            3: 4,
            4: 3,
            5: 1,
        }

        for player in odota_players_data:
            this_player_data = copy.deepcopy(default_player_data_dict)

            this_player_data['hero_id'] = player['hero_id']
            this_player_data['neutral_kills'] = player['neutral_kills']

            position = player['lane_role']
            self.positions[position].append(this_player_data)

        [values.sort(key=lambda x: x['neutral_kills']) for values in self.positions.values()]

        normalised = self._is_normalised()
        if not normalised:
            self._normalise()


    def _is_normalised(self) -> bool:
        for position, hero_ids in self.positions.items():
            if len(hero_ids) != 1:
                return False

        return True


    def _normalise_one(self):
        from_keys = []
        to_keys = []

        for position, hero_ids in self.positions.items():
            if len(hero_ids) > 1:
                from_keys.append(position)

            if len(hero_ids) < 1:
                to_keys.append(position)

        move_to = None

        from_keys.sort(key=_move_two_to_the_end)
        to_keys.sort(key=_move_two_to_the_end)

        for from_k in from_keys:
            if (priority_move := self._move_priority[from_k]):
                if priority_move in to_keys:
                    move_to = priority_move

            else:
                move_to = to_keys.pop(0) if to_keys[0] == 1 else to_keys.pop(-1)

            from_end = True if move_to < from_k else False

            self.positions[move_to].append(
                self.positions[from_k].pop(-1 if from_end else 0)
            )
            break


    def _normalise(self):
        while not self._is_normalised():
            self._normalise_one()


    def get_hero_to_positions(self) -> Dict[int, int]:
        return {v[0]['hero_id']: k for k, v in self.positions.items()}
