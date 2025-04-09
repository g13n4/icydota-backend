import copy
import json
import math
import pathlib
import re
from typing import Any, Optional, TypedDict

import pandas as pd
from fuzzywuzzy import fuzz

from constants.position import PositionConstant, POSITION_OPPONENTS
from models import PlayerGameData
from models.performance import PerformanceTotalData
from modules.match_windows_handler import MatchWindowsHandler
from utils import get_both_slot_values


class MatchPlayer(TypedDict, total=False):
    slot: int
    slot_text: str
    side: str

    hero_npc_name: str | None
    hero_npc_name_alias: str | None
    hero_name_cdota: str | None
    hero_id: int | None
    facet_id: int | None

    position: int | None
    position_id: int | None
    position_name: str | None

    player: str | None
    player_id: int | None

    team_id: int | None

    opponents: list[int]

    player_game_data: PlayerGameData | None
    performance_total_data: PerformanceTotalData | None


# MATCH PLAYER DATA
class MatchPlayersData:
    def __init__(self):
        for x in range(10):
            setattr(
                self, f'_{x}',
                MatchPlayer(
                    slot=x,
                    slot_text=f'_{x}',
                    side='sentinel' if x < 5 else 'dire',

                    hero_npc_name=None,
                    hero_npc_name_alias=None,
                    hero_name_cdota=None,
                    hero_id=None,
                    facet_id=None,

                    position=None,
                    position_id=None,
                    position_name=None,

                    player=None,
                    player_id=None,

                    opponents=[],

                    player_game_data=None,
                    performance_total_data=None,
                )
            )


    def update_slot_info(self, slot: int, **kwargs) -> None:
        info = getattr(self, f'_{slot}')
        setattr(self, f'_{slot}', { **info, **kwargs })


    def update_slot_name(self, slot: int, name: str) -> None:
        info = getattr(self, f'_{slot}')
        if not info['hero_npc_name']:
            info['hero_npc_name'] = name
        elif not info['hero_npc_name_alias']:
            info['hero_npc_name_alias'] = name
        else:
            raise ValueError('Hero has too many names!')

        setattr(self, f'_{slot}', info)


    def get_pos_to_slot_by_side(self) -> dict[str, dict[int, int]]:
        all_players = self.get_all()
        data = {
            'sentinel': dict(),
            'dire': dict(),
        }
        for player in all_players:
            data[player['side']][player['position']] = player['slot']

        return data


    def get_name_slot_dict(self) -> dict[str, int]:
        items = self.get_all()
        names = { x['hero_npc_name']: x['slot'] for x in items }
        alias = { x['hero_npc_name_alias']: x['slot'] for x in items if x['hero_npc_name_alias'] }
        return { **names, **alias }


    def get_all(self) -> list[MatchPlayer]:
        return [getattr(self, f'_{x}') for x in range(10)]


    def get_dire(self) -> list[MatchPlayer]:
        return [getattr(self, f'_{x}') for x in range(10) if x >= 5]


    def _get_by_name(self, key_name: str, value_name: str) -> MatchPlayer:
        for item in self.get_all():
            if item[key_name] == value_name:
                return item
        raise KeyError


    def get_by_cdata_name(self, name: str) -> MatchPlayer:
        return self._get_by_name('name_cdata', name)


    def get_by_ingame_name(self, name: str) -> MatchPlayer:
        return self._get_by_name('name_ingame', name)


    def __repr__(self):
        return '\n'.join([str(x) for x in self.get_all()])


    def __getitem__(self, slot: int) -> dict[str, Any]:
        if 0 <= slot < 10:
            return getattr(self, f'_{slot}')
        else:
            raise KeyError(f"No slot {slot}! Only ten players are in the game")


    def set_position_from_dict(self, positions: dict[str | int, int]):
        """
        :param positions: dictionary where key is the slot of the player and key is his position
        """
        for k, v in positions.items():
            slot_text, slot = get_both_slot_values(k)
            player = getattr(self, slot_text)
            player['position'] = v
            player['position_name'] = PositionConstant.POSITION_TO_NAME[v]
        self._set_opponents()


    def _new_data_check(self):
        test_player = getattr(self, '_0')
        if test_player['position']:
            self._set_position_names()
            self._set_opponents()


    def set_player_data_from_dict(self, players_info: dict[int, dict[str, Any]]):
        players = self.get_all()
        for player in players:
            player.update(players_info[player['slot']])
        self._new_data_check()


    def _set_position_names(self):
        players = self.get_all()
        for player in players:
            player['position_name'] = PositionConstant.POSITION_TO_NAME[player['position']]
        return


    def set_position_from_list(self, opponents: list[int]):
        players = self.get_all()
        for player, pos in zip(players, opponents):
            player['position'] = pos
            player['position_name'] = PositionConstant.POSITION_TO_NAME[pos]
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




class MatchAnalyser:
    def __init__(
            self,
            path: str | pathlib.Path,
            match_id: Optional[int] = None,
    ):
        self.path = path
        self.match_id = match_id

        self.players = MatchPlayersData()
        self._fill_cdata()
        self._fill_npc_data()
        self._game_total_length = None  # In game time aka the time the clock in the game is showing

        self._is_match_windows_set = False

        self.windows_handler = MatchWindowsHandler()

    def get_players(self) -> list[dict]:
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
        cdata_by_name = { x['hero_name_cdota']: x['slot'] for x in self.players.get_all() }
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


    @property
    def game_length(self) -> int:
        if self._is_match_windows_set:
            return self._game_total_length
        raise MatchAnalyserGameLengthException("Match windows are not created yet!")


    @property
    def match_windows(self) -> list[dict[str, Any]]:
        if self._is_match_windows_set:
            return copy.deepcopy(self.windows_handler.match_windows)
        raise MatchAnalyserWindowsException("Match windows are not created yet!")


    def get_match_data(self) -> dict[str, pd.DataFrame]:
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

        total_game_length = float("-inf")

        with open(self.path, 'r') as file:
            for line in file.readlines():
                for pattern in [
                    'epilogue',  #
                    'dotaplus',  # dota plus info
                    'cosmetics',  # items id's
                    'actions',  # button press
                    'DOTA_COMBATLOG_MODIFIER_ADD',  # add buff
                    'DOTA_COMBATLOG_MODIFIER_REMOVE',  # remove buff
                ]:
                    if re.search(pattern, line, re.IGNORECASE):
                        continue

                p_line = json.loads(line)
                line_type: str = p_line['type']
                line_time: int = p_line['time']

                # in new games the end games sets time to -855
                total_game_length = max(total_game_length, line_time)

                # the game hasn't started yet
                if line_time <= -90:
                    continue

                if line_type == 'interval':
                    interval.append(p_line)

                    self.windows_handler.update_time(line_time)

                if line_type == 'DOTA_COMBATLOG_GOLD' and p_line['gold_reason'] == 5:
                    break

                elif line_type == 'pings':
                    pings.append(p_line)

                elif line_type in ['sen_left', 'obs_left', 'obs', 'sen', ]:
                    if 'slot' not in p_line:
                        p_line['slot'] = wards_ehandle[p_line['ehandle']]

                    if line_type.endswith('_left'):
                        deward.append(
                            { x: p_line[x] for x in ['time', 'type', 'slot', 'entityleft', 'attackername', ] }
                        )
                    else:
                        wards.append({ x: p_line[x] for x in ['time', 'type', 'slot', ] })

                    wards_ehandle[p_line['ehandle']] = p_line['slot']


                # deprecated
                elif line_type in [
                    'CHAT_MESSAGE_ITEM_PURCHASE',
                    'CHAT_MESSAGE_RUNE_PICKUP',
                    'CHAT_MESSAGE_SCAN_USED',
                    'CHAT_MESSAGE_TOWER_KILL',
                    'CHAT_MESSAGE_COURIER_LOST',
                ]:
                    # chat_messages.append(p_line)
                    continue

                elif line_type in ['DOTA_COMBATLOG_DAMAGE', ]:
                    damage.append(p_line)

                elif line_type in ['DOTA_COMBATLOG_GOLD', ]:
                    gold.append(
                        { x: p_line[x] for x in
                          ['time', 'value', 'targetname', 'gold_reason'] }
                    )

                elif line_type in ['DOTA_COMBATLOG_XP', ]:
                    xp.append(
                        { x: p_line[x] for x in
                          ['time', 'value', 'targetname', 'xp_reason'] }
                    )

                elif line_type in ['DOTA_COMBATLOG_TEAM_BUILDING_KILL', ]:
                    building_kill.append(
                        { x: p_line[x] for x in
                          ['time', 'value', 'targetname'] }
                    )

                elif line_type == 'DOTA_COMBATLOG_DEATH' and p_line['targethero']:
                    hero_deaths.append({ x: p_line[x] for x in ['time', 'sourcename', 'targetname', ] })

                elif line_type == 'DOTA_COMBATLOG_DEATH' and p_line['targetname'] == 'npc_dota_roshan':
                    roshan_deaths.append({ x: p_line[x] for x in ['time', 'sourcename', ] })


        self._is_match_windows_set = True
        self._game_total_length = total_game_length
        self.windows_handler.set_window_status()


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
