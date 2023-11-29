from . import MatchPlayersData
from typing import Dict, List
import re
import pathlib
import json
import pandas as pd
from fuzzywuzzy import fuzz


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
        self.game_length = None

    def get_players(self) -> List[dict]:
        return self.players.get_all()

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
                        'hero_name_cdata': pline["unit"],
                        'hero_id': pline['hero_id'],
                    }

                    slots_added.add(pline["slot"])
                    self.players.update_slot_info(pline["slot"], **temp)

                if len(slots_added) == 10:
                    break
        return None

    def _combine_names(self, names: list):
        cdata_by_name = {x['hero_name_cdata']: x['slot'] for x in self.players.get_all()}
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

    def _update_game_length(self, time: int) -> None:
        if self.game_length is None or self.game_length < time:
            self.game_length = time

    def get_game_length(self) -> int:
        if self.game_length is None:
            raise ValueError('The game was not yet processed. Game length is unavailable')
        return self.game_length

    def get_match_data(self) -> Dict[str, pd.DataFrame]:
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

            # DOTA_COMBATLOG_DAMAGE
            # DOTA_COMBATLOG_GOLD
            # DOTA_COMBATLOG_XP
            # DOTA_COMBATLOG_PURCHASE
            # DOTA_COMBATLOG_ITEM
            # DOTA_COMBATLOG_TEAM_BUILDING_KILL
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
                from_cdata[item['hero_name_cdata']] = item

                from_ingame[item['hero_npc_name']] = item
                if item['hero_npc_name_alias']:
                    from_ingame[item['hero_npc_name_alias']] = item

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

                elif line_type == 'pings':
                    pings.append(p_line)

                elif line_type in ['obs', 'sen', ]:
                    wards.append({x: p_line[x] for x in
                                 ['time', 'type', 'slot', ]})

                elif line_type in ['sen_left', 'obs_left', ]:
                    deward.append({x: p_line[x] for x in
                                  ['time', 'type', 'slot', 'entityleft', 'attackername', ]})

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
                    self._update_game_length(p_line['time'])

                elif line_type in ['DOTA_COMBATLOG_GOLD', ]:
                    gold.append({x: p_line[x] for x in
                                 ['time', 'value', 'targetname', 'gold_reason']})

                elif line_type in ['DOTA_COMBATLOG_XP', ]:
                    xp.append({x: p_line[x] for x in
                               ['time', 'value', 'targetname', 'xp_reason']})

                elif line_type in ['DOTA_COMBATLOG_TEAM_BUILDING_KILL', ]:
                    building_kill.append({x: p_line[x] for x in
                                          ['time', 'value', 'targetname']})

                # deprecated
                elif line_type in ['DOTA_COMBATLOG_DAMAGE',
                                   'DOTA_COMBATLOG_GOLD',
                                   'DOTA_COMBATLOG_XP',
                                   'DOTA_COMBATLOG_PURCHASE',
                                   'DOTA_COMBATLOG_ITEM',
                                   'DOTA_COMBATLOG_TEAM_BUILDING_KILL',
                                   ]:
                    #                    combat_log.append(p_line)
                    continue

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
        }
