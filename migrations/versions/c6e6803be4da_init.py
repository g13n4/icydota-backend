"""init

Revision ID: c6e6803be4da
Revises: 
Create Date: 2024-01-16 12:51:35.626838

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c6e6803be4da'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('players',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('nickname', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('steam_id', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )
    op.create_table('positions',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('number', sa.Integer(), nullable=False),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )
    op.create_table('roshan_deaths',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('death_number', sa.Integer(), nullable=False),
                    sa.Column('death_time', sa.Integer(), nullable=False),
                    sa.Column('kill_dire', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )
    op.create_table('teams',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('odota_id', sa.Integer(), nullable=False),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('tag', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )
    op.create_table('heroes',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('odota_id', sa.Integer(), nullable=False),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('cdota_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('npc_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('npc_name_alias', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )
    op.create_table('leagues',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('pd_link', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('league_id', sa.Integer(), nullable=False),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('tier', sa.Integer(), nullable=False),
                    sa.Column('start_date', sa.Integer(), nullable=True),
                    sa.Column('end_date', sa.Integer(), nullable=True),
                    sa.Column('ended', sa.Boolean(), nullable=False),
                    sa.Column('fully_parsed', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )
    op.create_table('comparison_types',
                    sa.Column('player_cpd_id', sa.Integer(), nullable=False),
                    sa.Column('player_cps_id', sa.Integer(), nullable=False),
                    sa.Column('hero_cpd_id', sa.Integer(), nullable=False),
                    sa.Column('hero_cps_id', sa.Integer(), nullable=False),
                    sa.Column('pos_cpd_id', sa.Integer(), nullable=False),
                    sa.Column('pos_cps_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.ForeignKeyConstraint(['hero_cpd_id'], ['dota.heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['hero_cps_id'], ['dota.heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['player_cpd_id'], ['dota.players.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['player_cps_id'], ['dota.players.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['pos_cpd_id'], ['dota.positions.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['pos_cps_id'], ['dota.positions.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('player_cpd_id', 'player_cps_id', 'hero_cpd_id', 'hero_cps_id',
                                            'pos_cpd_id', 'pos_cps_id', 'id'),
                    schema='dota'
                    )
    op.create_table('performance_data_categories',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )
    op.create_table('data_aggregation_types',
                    sa.Column('player_id', sa.Integer(), nullable=False),
                    sa.Column('hero_id', sa.Integer(), nullable=False),
                    sa.Column('position_id', sa.Integer(), nullable=False),
                    sa.Column('data_info_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('by_player', sa.Boolean(), nullable=False),
                    sa.Column('by_hero', sa.Boolean(), nullable=False),
                    sa.Column('by_position', sa.Boolean(), nullable=False),
                    sa.ForeignKeyConstraint(['hero_id'], ['dota.heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['player_id'], ['dota.players.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['position_id'], ['dota.positions.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('player_id', 'hero_id', 'position_id', 'data_info_id', 'id'),
                    schema='dota'
                    )

    op.create_table('buildings_data',
                    sa.Column('not_destroyed_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('dire', sa.Boolean(), nullable=False),
                    sa.Column('destroyed_buildings', sa.Integer(), nullable=True),
                    sa.Column('destroyed_towers', sa.Integer(), nullable=True),
                    sa.Column('destroyed_rax', sa.Integer(), nullable=True),
                    sa.Column('destroyed_lane_1', sa.Boolean(), nullable=False),
                    sa.Column('destroyed_lane_2', sa.Boolean(), nullable=False),
                    sa.Column('destroyed_lane_3', sa.Boolean(), nullable=False),
                    sa.Column('megacreeps', sa.Boolean(), nullable=True),
                    sa.Column('naked_throne', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('not_destroyed_id', 'id'),
                    schema='dota'
                    )
    op.create_table('games_performance',
                    sa.Column('player_game_data_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.PrimaryKeyConstraint('player_game_data_id', 'id'),
                    schema='dota'
                    )
    op.create_table('in_game_buildings',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('lane', sa.Integer(), nullable=False),
                    sa.Column('is_tower', sa.Boolean(), nullable=False),
                    sa.Column('tier', sa.Integer(), nullable=True),
                    sa.Column('tower4', sa.Boolean(), nullable=True),
                    sa.Column('is_rax', sa.Boolean(), nullable=False),
                    sa.Column('melee', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )
    op.create_table('in_game_buildings_not_destroyed',
                    sa.Column('building_data_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('towers_left_top', sa.Integer(), nullable=False),
                    sa.Column('towers_left_mid', sa.Integer(), nullable=False),
                    sa.Column('towers_left_bottom', sa.Integer(), nullable=False),
                    sa.Column('towers_left_throne', sa.Integer(), nullable=False),
                    sa.Column('towers_left_total', sa.Integer(), nullable=False),
                    sa.Column('rax_left_top', sa.Integer(), nullable=False),
                    sa.Column('rax_left_mid', sa.Integer(), nullable=False),
                    sa.Column('rax_left_bottom', sa.Integer(), nullable=False),
                    sa.Column('rax_left_total', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('building_data_id', 'id'),
                    schema='dota'
                    )

    op.create_table('games_aggregated_data',
                    sa.Column('league_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.ForeignKeyConstraint(['league_id'], ['dota.leagues.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('league_id', 'id'),
                    schema='dota'
                    )
    op.create_table('hero_deaths',
                    sa.Column('killer_hero_id', sa.Integer(), nullable=False),
                    sa.Column('killer_player_id', sa.Integer(), nullable=False),
                    sa.Column('victim_hero_id', sa.Integer(), nullable=False),
                    sa.Column('victim_player_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('death_number', sa.Integer(), nullable=False),
                    sa.Column('death_time', sa.Integer(), nullable=False),
                    sa.Column('kill_dire', sa.Boolean(), nullable=True),
                    sa.Column('victim_dire', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(['killer_hero_id'], ['dota.heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['killer_player_id'], ['dota.players.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['victim_hero_id'], ['dota.heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['victim_player_id'], ['dota.players.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('killer_hero_id', 'killer_player_id', 'victim_hero_id', 'victim_player_id',
                                            'id'),
                    schema='dota'
                    )
    op.create_table('in_game_buildings_destroyed',
                    sa.Column('building_id', sa.Integer(), nullable=False),
                    sa.Column('building_data_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('death_time', sa.Integer(), nullable=False),
                    sa.Column('destruction_order', sa.Integer(), nullable=True),
                    sa.Column('destruction_order_tower', sa.Integer(), nullable=True),
                    sa.Column('destruction_order_rax', sa.Integer(), nullable=True),
                    sa.Column('destroyed_lane_1', sa.Boolean(), nullable=False),
                    sa.Column('destroyed_lane_2', sa.Boolean(), nullable=False),
                    sa.Column('destroyed_lane_3', sa.Boolean(), nullable=False),
                    sa.Column('megacreeps', sa.Boolean(), nullable=False),
                    sa.Column('naked_throne', sa.Boolean(), nullable=False),
                    sa.ForeignKeyConstraint(['building_id'], ['dota.in_game_buildings.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('building_id', 'building_data_id', 'id'),
                    schema='dota'
                    )
    op.create_table('performance_data_types',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('data_category_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['data_category_id'], ['dota.performance_data_categories.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )

    op.create_table('performance_totals_data',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('data_info_id', sa.Integer(), nullable=True),
                    sa.Column('total_gold', sa.Integer(), nullable=False),
                    sa.Column('total_xp', sa.Integer(), nullable=False),
                    sa.Column('kills_per_min', sa.Integer(), nullable=False),
                    sa.Column('kda', sa.Integer(), nullable=False),
                    sa.Column('neutral_kills', sa.Integer(), nullable=False),
                    sa.Column('tower_kills', sa.Integer(), nullable=False),
                    sa.Column('courier_kills', sa.Integer(), nullable=False),
                    sa.Column('lane_kills', sa.Integer(), nullable=False),
                    sa.Column('hero_kills', sa.Integer(), nullable=False),
                    sa.Column('observer_kills', sa.Integer(), nullable=False),
                    sa.Column('sentry_kills', sa.Integer(), nullable=False),
                    sa.Column('roshan_kills', sa.Integer(), nullable=False),
                    sa.Column('runes_picked_up', sa.Integer(), nullable=False),
                    sa.Column('ancient_kills', sa.Integer(), nullable=False),
                    sa.Column('buyback_count', sa.Integer(), nullable=False),
                    sa.Column('observer_uses', sa.Integer(), nullable=False),
                    sa.Column('sentry_uses', sa.Integer(), nullable=False),
                    sa.Column('lane_efficiency', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('lane_efficiency_pct', sa.Integer(), nullable=False),
                    sa.Column('first_blood_claimed', sa.Boolean(), nullable=True),
                    sa.Column('first_kill_time', sa.Integer(), nullable=True),
                    sa.Column('died_first', sa.Boolean(), nullable=True),
                    sa.Column('first_death_time', sa.Integer(), nullable=True),
                    sa.Column('lost_tower_first', sa.Boolean(), nullable=True),
                    sa.Column('lost_tower_lane', sa.Integer(), nullable=True),
                    sa.Column('lost_tower_time', sa.Integer(), nullable=True),
                    sa.Column('destroyed_tower_first', sa.Boolean(), nullable=True),
                    sa.Column('destroyed_tower_lane', sa.Integer(), nullable=True),
                    sa.Column('destroyed_tower_time', sa.Integer(), nullable=True),
                    sa.Column('game_performance_id', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )
    op.create_table('performance_windows_data',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('data_info_id', sa.Integer(), nullable=True),
                    sa.Column('l2', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('l4', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('l6', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('l8', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('l10', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('ltotal', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('g15', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('g30', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('g45', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('g60', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('g60plus', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('gtotal', sa.Numeric(precision=10, scale=2), nullable=True),
                    sa.Column('game_performance_id', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )
    op.create_table('games',
                    sa.Column('league_id', sa.Integer(), nullable=False),
                    sa.Column('sent_team_id', sa.Integer(), nullable=False),
                    sa.Column('dire_team_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('match_id', sa.Integer(), nullable=False),
                    sa.Column('dire_win', sa.Boolean(), nullable=False),
                    sa.Column('average_roshan_window_time', sa.Integer(), nullable=True),
                    sa.Column('first_ten_kills_dire', sa.Boolean(), nullable=False),
                    sa.Column('dire_lost_first_tower', sa.Boolean(), nullable=False),
                    sa.Column('dire_building_status_id', sa.Integer(), nullable=True),
                    sa.Column('sent_building_status_id', sa.Integer(), nullable=True),
                    sa.Column('game_start_time', sa.Integer(), nullable=False),
                    sa.Column('duration', sa.Integer(), nullable=False),
                    sa.Column('replay_url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.ForeignKeyConstraint(['dire_team_id'], ['dota.teams.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['sent_team_id'], ['dota.teams.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['league_id'], ['dota.leagues.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('league_id', 'sent_team_id', 'dire_team_id', 'id',
                                            'sent_building_status_id', 'dire_building_status_id'),
                    schema='dota'
                    )
    op.create_table('player_games_data',
                    sa.Column('team_id', sa.Integer(), nullable=False),
                    sa.Column('player_id', sa.Integer(), nullable=False),
                    sa.Column('position_id', sa.Integer(), nullable=False),
                    sa.Column('hero_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('nickname', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('slot', sa.Integer(), nullable=False),
                    sa.Column('lane', sa.Integer(), nullable=False),
                    sa.Column('is_roaming', sa.Boolean(), nullable=False),
                    sa.Column('win', sa.Boolean(), nullable=False),
                    sa.Column('dire', sa.Boolean(), nullable=False),
                    sa.Column('rank', sa.Integer(), nullable=False),
                    sa.Column('apm', sa.Integer(), nullable=False),
                    sa.Column('pings', sa.Integer(), nullable=False),
                    sa.Column('performance_id', sa.Integer(), nullable=True),
                    sa.Column('game_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['game_id'], ['dota.games.id'], ),
                    sa.ForeignKeyConstraint(['hero_id'], ['dota.heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['performance_id'], ['dota.games_performance.id'], ),
                    sa.ForeignKeyConstraint(['player_id'], ['dota.players.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['position_id'], ['dota.positions.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['team_id'], ['dota.teams.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('team_id', 'player_id', 'position_id', 'hero_id', 'id'),
                    schema='dota'
                    )
    op.create_table('games_aggregated_by_hero',
                    sa.Column('window_stats_id', sa.Integer(), nullable=False),
                    sa.Column('game_aggregated_data_id', sa.Integer(), nullable=False),
                    sa.Column('hero_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.ForeignKeyConstraint(['game_aggregated_data_id'], ['dota.games_aggregated_data.id'],
                                            ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['hero_id'], ['dota.heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['window_stats_id'], ['dota.player_games_data.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('window_stats_id', 'game_aggregated_data_id', 'hero_id', 'id'),
                    schema='dota'
                    )
    op.create_table('games_aggregated_by_player',
                    sa.Column('window_stats_id', sa.Integer(), nullable=False),
                    sa.Column('game_aggregated_data_id', sa.Integer(), nullable=False),
                    sa.Column('player_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.ForeignKeyConstraint(['game_aggregated_data_id'], ['dota.games_aggregated_data.id'],
                                            ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['player_id'], ['dota.players.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['window_stats_id'], ['dota.player_games_data.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('window_stats_id', 'game_aggregated_data_id', 'player_id', 'id'),
                    schema='dota'
                    )
    op.create_table('games_aggregated_by_position',
                    sa.Column('window_stats_id', sa.Integer(), nullable=False),
                    sa.Column('game_aggregated_data_id', sa.Integer(), nullable=False),
                    sa.Column('position_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.ForeignKeyConstraint(['game_aggregated_data_id'], ['dota.games_aggregated_data.id'],
                                            ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['position_id'], ['dota.positions.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['window_stats_id'], ['dota.player_games_data.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('window_stats_id', 'game_aggregated_data_id', 'position_id', 'id'),
                    schema='dota'
                    )
    op.create_table('performance_data_descriptions',
                    sa.Column('id', sa.Integer(), nullable=False, unique=True),
                    sa.Column('data_type_id', sa.Integer(), nullable=True),
                    sa.Column('is_total_stats', sa.Boolean(), nullable=False),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('is_comparison', sa.Boolean(), nullable=False),
                    sa.Column('comparison_id', sa.Integer(), nullable=True),
                    sa.Column('is_aggregation', sa.Boolean(), nullable=False),
                    sa.Column('aggregation_id', sa.Integer(), nullable=True),
                    sa.Column('performance_window_data_id', sa.Integer(), nullable=True),
                    sa.Column('performance_total_data_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['aggregation_id'], ['dota.data_aggregation_types.id'], ),
                    sa.ForeignKeyConstraint(['comparison_id'], ['dota.comparison_types.id'], ),
                    sa.ForeignKeyConstraint(['data_type_id'], ['dota.performance_data_types.id'], ),
                    sa.ForeignKeyConstraint(['performance_total_data_id'], ['dota.performance_totals_data.id'], ),
                    sa.ForeignKeyConstraint(['performance_window_data_id'], ['dota.performance_windows_data.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    schema='dota'
                    )

    # ### end Alembic commands ###
    op.create_foreign_key(
        'fk_buildings_data__in_game_buildings_not_destroyed',
        'buildings_data', 'in_game_buildings_not_destroyed',
        ['not_destroyed_id'], ['id'], ondelete='SET NULL',
        source_schema='dota', referent_schema='dota',
    )
    op.create_foreign_key(
        'fk_games_performance__player_games_data',
        'games_performance', 'player_games_data',
        ['player_game_data_id'], ['id'], ondelete='SET NULL',
        source_schema='dota', referent_schema='dota',
    )
    op.create_foreign_key(
        'fk_in_game_buildings_not_destroyed__buildings_data',
        'in_game_buildings_not_destroyed', 'buildings_data',
        ['building_data_id'], ['id'], ondelete='SET NULL',
        source_schema='dota', referent_schema='dota',
    )
    op.create_foreign_key(
        'fk_data_aggregation_types__performance_data_descriptions',
        'data_aggregation_types', 'performance_data_descriptions',
        ['data_info_id'], ['id'], ondelete='SET NULL',
        source_schema='dota', referent_schema='dota',
    )
    op.create_foreign_key(
        'fk_in_game_buildings_destroyed__buildings_data',
        'in_game_buildings_destroyed', 'buildings_data',
        ['building_data_id'], ['id'], ondelete='SET NULL',
        source_schema='dota', referent_schema='dota',
    )

    op.create_foreign_key(
        'fk_performance_totals_data__performance_data_descriptions',
        'performance_totals_data', 'performance_data_descriptions',
        ['data_info_id'], ['id'], ondelete='SET NULL',
        source_schema='dota', referent_schema='dota',
    )
    op.create_foreign_key(
        'fk_performance_windows_data__performance_data_descriptions',
        'performance_windows_data', 'performance_data_descriptions',
        ['data_info_id'], ['id'], ondelete='SET NULL',
        source_schema='dota', referent_schema='dota',
    )
    op.create_foreign_key(
        'fk_performance_totals_data__games_performance',
        'performance_totals_data', 'games_performance',
        ['game_performance_id'], ['id'], ondelete='SET NULL',
        source_schema='dota', referent_schema='dota',
    )
    op.create_foreign_key(
        'fk_performance_windows_data__games_performance',
        'performance_windows_data', 'games_performance',
        ['game_performance_id'], ['id'], ondelete='SET NULL',
        source_schema='dota', referent_schema='dota',
    )

    op.create_foreign_key(
        'fk_games_dire__buildings_data',
        'games', 'buildings_data',
        ['dire_building_status_id'], ['id'], ondelete='SET NULL',
        source_schema='dota', referent_schema='dota',
    )
    op.create_foreign_key(
        'fk_games_sent__buildings_data',
        'games', 'buildings_data',
        ['sent_building_status_id'], ['id'], ondelete='SET NULL',
        source_schema='dota', referent_schema='dota',
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('performance_data_types', schema='dota')
    op.drop_table('in_game_buildings_destroyed', schema='dota')
    op.drop_table('hero_deaths', schema='dota')
    op.drop_table('games_aggregated_data', schema='dota')
    op.drop_table('games_aggregated_by_position', schema='dota')
    op.drop_table('games_aggregated_by_player', schema='dota')
    op.drop_table('games_aggregated_by_hero', schema='dota')
    op.drop_table('games', schema='dota')
    op.drop_table('data_aggregation_types', schema='dota')
    op.drop_table('comparison_types', schema='dota')
    op.drop_table('teams', schema='dota')
    op.drop_table('roshan_deaths', schema='dota')
    op.drop_table('positions', schema='dota')
    op.drop_table('players', schema='dota')
    op.drop_table('player_games_data', schema='dota')
    op.drop_table('performance_windows_data', schema='dota')
    op.drop_table('performance_totals_data', schema='dota')
    op.drop_table('performance_data_descriptions', schema='dota')
    op.drop_table('performance_data_categories', schema='dota')
    op.drop_table('leagues', schema='dota')
    op.drop_table('in_game_buildings_not_destroyed', schema='dota')
    op.drop_table('in_game_buildings', schema='dota')
    op.drop_table('heroes', schema='dota')
    op.drop_table('games_performance', schema='dota')
    op.drop_table('buildings_data', schema='dota')
    # ### end Alembic commands ###
