import copy
import json
import math
import pathlib
import re
from typing import Dict, List, Any, Tuple, Optional

import pandas as pd
from fuzzywuzzy import fuzz

from replay_parsing.ingame_data import POSITION_NAMES, POSITION_OPPONENTS
from utils import get_both_slot_values


# MATCH PLAYER DATA
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
                if player['side'] == opponent['side'] or opponent['position'] not in player_opponents_positions:
                    continue

                player['opponents'].append(opponent['slot'])


# MATCH ANALYSER
class MatchAnalyserWindowsException(Exception):
    pass


class MatchAnalyserGameLengthException(Exception):
    pass


def _process_name(text: str) -> str:
    for pattern in ['npc_dota_hero_', 'CDOTA_Unit_Hero_', '_']:
        text = re.sub(pattern, '', text)
    return text.lower()


def _compare_name_simple(cdota_name, npc_name) -> bool:
    cdota_name_processed = _process_name(cdota_name)
    npc_name_processed = _process_name(npc_name)
    return cdota_name_processed == npc_name_processed


def _compare_name_complex(cdota_name, npc_name) -> int:
    cdota_name_processed = _process_name(cdota_name)
    npc_name_processed = _process_name(npc_name)

    return fuzz.ratio(cdota_name_processed, npc_name_processed)


early_game_windows = [(1, 'l2', 'lane', -90, 60 * 2,),  # first 2 minutes
                      (2, 'l4', 'lane', 60 * 2, 60 * 4,),  # 2-4
                      (3, 'l6', 'lane', 60 * 4, 60 * 6,),  # 4-6
                      (4, 'l8', 'lane', 60 * 6, 60 * 8,),  # 6-8
                      (5, 'l10', 'lane', 60 * 8, 60 * 10,), ]  # 8-10

late_game_windows = [(1, 'g15', 'game', -90, 60 * 15,),  # first 15 minutes
                     (2, 'g30', 'game', 60 * 15, 60 * 30,),  # 15 - 30
                     (3, 'g45', 'game', 60 * 30, 60 * 45,),  # 30 - 45
                     (4, 'g60', 'game', 60 * 45, 60 * 60,),  # 45 - 60
                     (5, 'g60plus', 'game', 60 * 60, 60 * 60 * 60,), ]  # 60 - inf


class MatchAnalyser:
    def __init__(self,
                 path: str | pathlib.Path,
                 windows: List[Tuple[int, int, str]] = None,
                 match_id: Optional[int] = None, ):
        self.path = path
        self.match_id = match_id

        self.players = MatchPlayersData()
        self._fill_cdata()
        self._fill_npc_data()
        self._game_total_length = None  # In game time aka the time the clock in the game is showing

        self._is_match_windows_set = False

        if not windows:
            windows = early_game_windows + late_game_windows

        self._match_windows = [{'name': window[1],
                                'window_type': window[2],
                                'index': window[0],

                                'start_time': None,
                                'end_time': None,

                                'window_start': window[3],
                                'window_end': window[4],
                                'window_length': window[4] - window[3],

                                'length': 0,
                                'minutes': 0,

                                'exists': False,
                                'empty': None,
                                'incomplete': False,
                                'df': None, } for window in windows]

        self._windows_types = list(set([window['window_type'] for window in self._match_windows]))


    def get_players(self) -> List[dict]:
        return self.players.get_all()


    def get_players_object(self) -> MatchPlayersData:
        return self.players


    def _fill_cdata(self) -> None:
        slots_added = set()
        re_interval = re.compile(r'"interval"')
        with open(self.path, 'r') as file:
            for line in file.readlines():
                if not re_interval.search(line):
                    continue

                pline = json.loads(line)
                if pline.get("hero_id", None) and pline['slot'] not in slots_added:
                    temp = {
                        'hero_name_cdota': pline["unit"],
                        'hero_id': pline['hero_id'],
                    }

                    slots_added.add(pline["slot"])
                    self.players.update_slot_info(pline["slot"], **temp)

                if len(slots_added) == 10:
                    break
        return None


    def _combine_names(self, names: list):
        cdata_by_name = {x['hero_name_cdota']: x['slot'] for x in self.players.get_all()}
        most_fitting_word = None

        for npc_name in names:
            for k_cdota_name, v_slot in cdata_by_name.items():
                most_fitting_word = {
                    'score': 0,
                    'word': '',
                    'slot': None,
                    'found': False,
                }

                if _compare_name_simple(npc_name, k_cdota_name):
                    self.players.update_slot_name(v_slot, npc_name)
                    most_fitting_word['found'] = True
                    break

                ratio = _compare_name_complex(k_cdota_name, npc_name)
                if ratio > most_fitting_word['score']:
                    most_fitting_word['score'] = ratio
                    most_fitting_word['word'] = npc_name
                    most_fitting_word['slot'] = v_slot

            if not most_fitting_word['found']:
                self.players.update_slot_name(most_fitting_word['slot'], most_fitting_word['word'])


    def _fill_npc_data(self) -> None:
        npc_names = set()
        re_hero_name = re.compile('"(npc_dota_hero_.*?)"')
        with open(self.path, 'r') as file:
            for line in file.readlines():
                for name in re_hero_name.findall(line):
                    npc_names.add(name)

        self._combine_names(list(npc_names))
        return None


    def _update_game_time_data(self,
                               current_window_index: int | None,
                               time: int) -> int:
        self._game_total_length = time

        if current_window_index is None or time < self._match_windows[0]['window_start']:
            return 0

        current_window = self._match_windows[current_window_index]
        window_start = current_window['window_start']
        window_end = current_window['window_end']

        if window_start <= time < window_end:
            if not current_window['start_time']:
                current_window['start_time']: int = time
                current_window['exists'] = True

            current_window['end_time']: int = time

            # one second offset to ensure that a one second window exists
            current_window['length'] = current_window['end_time'] - current_window['start_time'] + 1
            current_window['minutes'] = math.ceil(current_window['length'] / 60)

            return current_window_index
        else:
            return self._update_game_time_data(current_window_index + 1, time)


    @property
    def game_length(self) -> int:
        if self._is_match_windows_set:
            return self._game_total_length
        raise MatchAnalyserGameLengthException("Match windows are not created yet!")


    @property
    def match_windows(self) -> List[Dict[str, Any]]:
        if self._is_match_windows_set:
            return copy.deepcopy(self._match_windows)
        raise MatchAnalyserWindowsException("Match windows are not created yet!")


    def _set_incomplete_status(self, ) -> None:
        for window_type in self._windows_types:
            for window in self._match_windows:
                if not window['window_type'] == window_type:
                    pass

                if window['length'] > 0 and \
                        not (window['window_length'] + 2 > window['length'] > window['window_length'] - 2):
                    window['incomplete'] = True
                    break


    def get_match_data(self) -> Dict[str, pd.DataFrame]:
        current_window_index = None

        interval = []  # interval
        pings = []  # pings
        wards = []  # obs / sen / sen_left / obs_left
        deward = []  # sen_left / obs_left

        # CHAT_MESSAGE_ITEM_PURCHASE
        # CHAT_MESSAGE_RUNE_PICKUP
        # CHAT_MESSAGE_SCAN_USED
        # CHAT_MESSAGE_TOWER_KILL
        # CHAT_MESSAGE_COURIER_LOST
        # chat_messages = []

        # DOTA_COMBATLOG_DEATH
        hero_deaths = []

        roshan_deaths = []

        # DOTA_COMBATLOG_DAMAGE
        # DOTA_COMBATLOG_GOLD
        # DOTA_COMBATLOG_XP
        # DOTA_COMBATLOG_PURCHASE
        # DOTA_COMBATLOG_ITEM
        # combat_log = []

        # DOTA_COMBATLOG_TEAM_BUILDING_KILL
        building_kill = []

        # DOTA_COMBATLOG_XP
        xp = []

        # DOTA_COMBATLOG_DAMAGE
        damage = []

        # DOTA_COMBATLOG_GOLD
        gold = []

        from_cdata = dict()
        from_ingame = dict()

        for item in self.players.get_all():
            from_cdata[item['hero_name_cdota']] = item

            from_ingame[item['hero_npc_name']] = item
            if item['hero_npc_name_alias']:
                from_ingame[item['hero_npc_name_alias']] = item

        wards_ehandle = dict()

        with open(self.path, 'r') as file:
            for line in file.readlines():
                for pattern in ['"epilogue"',  #
                                '"dotaplus"',  # dota plus info
                                '"cosmetics"',  # items id's
                                '"actions"',  # button press
                                '"DOTA_COMBATLOG_MODIFIER_ADD"',  # add buff
                                '"DOTA_COMBATLOG_MODIFIER_REMOVE"', ]:  # remove buff

                    if re.search(pattern, line, re.IGNORECASE):
                        continue

                p_line = json.loads(line)
                line_type: str = p_line['type']
                line_time: int = p_line['time']

                if line_time <= -90:
                    continue

                if line_type == 'interval':
                    interval.append(p_line)

                    current_window_index = self._update_game_time_data(current_window_index=current_window_index,
                                                                       time=line_time, )

                if line_type == 'DOTA_COMBATLOG_GOLD' and p_line['gold_reason'] == 5:
                    break

                elif line_type == 'pings':
                    pings.append(p_line)

                elif line_type in ['sen_left', 'obs_left', 'obs', 'sen', ]:
                    if 'slot' not in p_line:
                        p_line['slot'] = wards_ehandle[p_line['ehandle']]

                    if line_type.endswith('_left'):
                        deward.append({x: p_line[x] for x in ['time', 'type', 'slot', 'entityleft', 'attackername', ]})
                    else:
                        wards.append({x: p_line[x] for x in ['time', 'type', 'slot', ]})

                    wards_ehandle[p_line['ehandle']] = p_line['slot']


                # deprecated
                elif line_type in ['CHAT_MESSAGE_ITEM_PURCHASE',
                                   'CHAT_MESSAGE_RUNE_PICKUP',
                                   'CHAT_MESSAGE_SCAN_USED',
                                   'CHAT_MESSAGE_TOWER_KILL',
                                   'CHAT_MESSAGE_COURIER_LOST', ]:
                    # chat_messages.append(p_line)
                    continue

                elif line_type in ['DOTA_COMBATLOG_DAMAGE', ]:
                    damage.append(p_line)

                elif line_type in ['DOTA_COMBATLOG_GOLD', ]:
                    gold.append({x: p_line[x] for x in
                                 ['time', 'value', 'targetname', 'gold_reason']})

                elif line_type in ['DOTA_COMBATLOG_XP', ]:
                    xp.append({x: p_line[x] for x in
                               ['time', 'value', 'targetname', 'xp_reason']})

                elif line_type in ['DOTA_COMBATLOG_TEAM_BUILDING_KILL', ]:
                    building_kill.append({x: p_line[x] for x in
                                          ['time', 'value', 'targetname']})

                elif line_type == 'DOTA_COMBATLOG_DEATH' and p_line['targethero']:
                    hero_deaths.append({x: p_line[x] for x in ['time', 'sourcename', 'targetname', ]})

                elif line_type == 'DOTA_COMBATLOG_DEATH' and p_line['targetname'] == 'npc_dota_roshan':
                    roshan_deaths.append({x: p_line[x] for x in ['time', 'sourcename', ]})

        self._is_match_windows_set = True
        self._set_incomplete_status()

        return {
            'interval': pd.DataFrame(interval),
            'pings': pd.DataFrame(pings),
            'wards': pd.DataFrame(wards),
            'deward': pd.DataFrame(deward),
            # 'chat_messages': pd.DataFrame(chat_messages),
            #  'combat_log': pd.DataFrame(combat_log),
            'building_kill': pd.DataFrame(building_kill),
            'xp': pd.DataFrame(xp),
            'gold': pd.DataFrame(gold),
            'damage': pd.DataFrame(damage),
            'roshan_deaths': pd.DataFrame(roshan_deaths),
            'hero_deaths': pd.DataFrame(hero_deaths),
        }
