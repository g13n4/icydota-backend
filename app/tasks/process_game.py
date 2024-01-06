from typing import Dict, List

from sqlmodel import select

from utils import get_all_sqlmodel_objs
from .download_replay import get_match_replay
from .proces_game_replay import process_game_replay
from ..celery import celery_app
from ..models import InGamePosition, Hero
from ..models import Player, Team, League
from ..models import PlayerGameInfo, Game, PerformanceTotalData


def process_teams(db_session, dire_data: dict, radiant_data: dict) -> Dict[str, Team]:
    teams = {
        'radiant': radiant_data,
        'dire': dire_data,
    }

    obj_teams = {
        'radiant': None,
        'dire': None,
    }

    for key, data in teams.items():
        team_obj = db_session.execute(select(Team).where(Team.odota_id == data['team_id'])).first()
        if not team_obj:
            team_obj = Team(
                odota_id=data['team_id'],
                name=data['name'],
                tag=data['tag'],
            )
            db_session.add(team_obj)

        obj_teams[key] = team_obj

    db_session.commit()
    return obj_teams


def process_players(db_session, players: List[dict]) -> Dict[int, Player]:
    players_dict: dict = {x: None for x in range(10)}

    for player in players:
        player_obj = db_session.execute(select(Player).where(Player.steam_id == player['account_id'])).first()
        if not player_obj:
            player_obj = Player(
                nickname=player['name'],
                steam_id=player['account_id']
            )
            db_session.add(player_obj)

        players_dict[players_dict['player_slot']] = player_obj

    db_session.commit()
    return players_dict


def create_game_obj(db_session, league_obj: League, game_data: dict, teams: dict) -> Game:
    game_obj = Game(
        match_id=game_data['match_id'],

        league=league_obj,

        patch=game_data['patch'],

        radiant_team=teams['radiant'].id,
        dire_team=teams['dire'].id,
        radiant_win=game_data['radiant_win'],

        game_start_time=game_data['start_time'],
        duration=game_data['duration'],
        replay_url=game_data['replay_url'],
    )

    db_session.add(game_obj)
    db_session.commit()
    db_session.refresh(game_obj)
    return game_obj


@celery_app.task
def process_game(db_session, web_client, match_id: int, league_obj: League):
    r = web_client.get(f'https://api.opendota.com/api/matches/{match_id}')
    game_data = r.json()

    teams_dict = process_teams(db_session, game_data['dire_team'], game_data['radiant_team'])
    players_dict = process_players(db_session, game_data['players'])

    game_obj = create_game_obj(db_session,
                               league_obj=league_obj,
                               game_data=game_data,
                               teams=teams_dict)

    positions_all = get_all_sqlmodel_objs(db_session, InGamePosition)
    positions_dict = {x.number: x for x in positions_all}  # "lane_role": 3,

    heroes_all = get_all_sqlmodel_objs(db_session, Hero)
    heroes_dict = {x.odota_id: x for x in heroes_all}  # "hero_id": 78,

    player_data_dict = dict()
    pperformance_total_dict = dict()
    ppositions_dict = dict()
    wp_dict = dict()
    pgi_dict = {}
    for player_info in game_data['players']:
        this_team = teams_dict['radiant'] if player_info['isRadiant'] else teams_dict['dire']
        this_slot = player_info['player_slot']
        this_position = player_info['lane_role']
        this_hero = player_info['hero_id']

        player_obj = PlayerGameInfo(
            team=this_team,
            player_id=players_dict[this_slot].id,
            nickname=player_info['name'],

            position_id=positions_dict[this_position].id,
            hero_id=heroes_dict[this_hero].id,
            lane=player_info['lane'],
            is_roaming=player_info['is_roaming'],

            win=player_info['win'],
            dire=(not player_info['isRadiant']),

            rank=player_info['rank_tier'],
            apm=player_info['actions_per_min'],
            slot=this_slot,
            pings=player_info['pings'],

            game=game_obj,
        )

        pgi_dict[this_slot] = player_obj

        db_session.add(player_obj)

        player_data_dict[this_slot] = {
            'position': positions_dict[this_position].value,
            'hero_id': heroes_dict[this_hero].id,
            'player_id': players_dict[this_slot].id,

        }
        ppositions_dict[this_slot] = positions_dict[this_position]

        p_per_tot_stats_obj = PerformanceTotalData(
            total_gold=player_info['total_gold'],
            total_xp=player_info['total_xp'],
            kills_per_min=player_info['benchmarks']['kills_per_min'],
            kda=player_info['kda'],

            neutral_kills=player_info['neutral_kills'],
            tower_kills=player_info['tower_kills'],
            courier_kills=player_info['courier_kills'],

            lane_kills=player_info['lane_kills'],
            hero_kills=player_info['hero_kills'],
            observer_kills=player_info['observer_kills'],
            sentry_kills=player_info['sentry_kills'],
            roshan_kills=player_info['roshan_kills'],
            runes_picked_up=player_info['rune_pickups'],

            ancient_kills=player_info['ancient_kills'],
            buyback_count=player_info['buyback_count'],
            observer_uses=player_info['observer_uses'],
            sentry_uses=player_info['sentry_uses'],

            lane_efficiency=player_info['lane_efficiency'],
            lane_efficiency_pct=player_info['lane_efficiency_pct'],

            # first_death_time fill later
            # first_kill_time fill later

            # first_blood_claimed=player_info['rune_pickups'],
            # died_first=player_info['rune_pickups'],
        )

        db_session.add(p_per_tot_stats_obj)

        pperformance_total_dict[this_slot] = p_per_tot_stats_obj

    db_session.commit()

    get_match_replay(match_id=match_id, )

    process_game_replay(db_session=db_session,
                        match_id=match_id,
                        game_obj=game_obj,
                        pperformance_objs=pperformance_total_dict,
                        pgi_dict=pgi_dict,
                        additional_player_data=player_data_dict)
