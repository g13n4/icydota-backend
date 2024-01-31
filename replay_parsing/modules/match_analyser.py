import copy
import json
import math
import pathlib
import re
from typing import Dict, List, Any

import pandas as pd
from fuzzywuzzy import fuzz

from . import MatchPlayersData
from .match_windows import GAME_WINDOWS


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


class MatchAnalyser:
    def __init__(self, path: str | pathlib.Path):
        self.path = path

        self.players = MatchPlayersData()
        self._fill_cdata()
        self._fill_npc_data()
        self._game_total_length = None  # In game time aka the time the clock in the game is showing

        self._is_match_windows_set = False
        self._match_windows = [{'name': window[2],

                                'start_time': None,
                                'end_time': None,

                                'window_start': window[0],
                                'window_end': window[1],

                                'length': 0,
                                'minutes': 0,

                                'exists': False,
                                'empty': None,
                                'df': None, } for window in GAME_WINDOWS]


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
            self._update_game_time_data(current_window_index + 1, time)


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


    def get_match_data(self) -> Dict[str, pd.DataFrame]:
        current_window_index = None

        with open(self.path, 'r') as file:
            interval = []  # interval
            pings = []  # pings
            wards = []  # obs / sen / sen_left / obs_left
            deward = []  # sen_left / obs_left
            # CHAT_MESSAGE_ITEM_PURCHASE
            # CHAT_MESSAGE_RUNE_PICKUP
            # CHAT_MESSAGE_SCAN_USED
            # CHAT_MESSAGE_TOWER_KILL
            # CHAT_MESSAGE_COURIER_LOST
            chat_messages = []

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
                line_type = p_line['type']

                if line_type == 'interval' and p_line['time'] > -90:
                    interval.append(p_line)

                    current_window_index = self._update_game_time_data(current_window_index=current_window_index,
                                                                       time=p_line['time'], )

                elif line_type == 'pings':
                    pings.append(p_line)

                elif line_type in ['obs', 'sen', ]:
                    wards.append({x: p_line[x] for x in ['time', 'type', 'slot', ]})

                    wards_ehandle[p_line['ehandle']] = p_line['slot']

                elif line_type in ['sen_left', 'obs_left', ]:
                    if 'slot' not in p_line:
                        p_line['slot'] = wards_ehandle[p_line['ehandle']]

                    deward.append({x: p_line[x] for x in ['time', 'type', 'slot', 'entityleft', 'attackername', ]})

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
