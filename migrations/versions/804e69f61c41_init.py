"""init

Revision ID: 804e69f61c41
Revises: 
Create Date: 2024-02-19 02:00:27.467381

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '804e69f61c41'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('heroes',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('cdota_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('npc_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('npc_name_alias', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_heroes_name'), 'heroes', ['name'], unique=True)
    op.create_table('in_game_buildings',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('lane', sa.Integer(), nullable=False),
                    sa.Column('is_tower', sa.Boolean(), nullable=False),
                    sa.Column('tier', sa.Integer(), nullable=True),
                    sa.Column('tower4', sa.Boolean(), nullable=True),
                    sa.Column('is_rax', sa.Boolean(), nullable=True),
                    sa.Column('melee', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('in_game_buildings_not_destroyed',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('towers_left_top', sa.Integer(), nullable=False),
                    sa.Column('towers_left_mid', sa.Integer(), nullable=False),
                    sa.Column('towers_left_bottom', sa.Integer(), nullable=False),
                    sa.Column('towers_left_throne', sa.Integer(), nullable=False),
                    sa.Column('towers_left_total', sa.Integer(), nullable=False),
                    sa.Column('rax_left_top', sa.Integer(), nullable=False),
                    sa.Column('rax_left_mid', sa.Integer(), nullable=False),
                    sa.Column('rax_left_bottom', sa.Integer(), nullable=False),
                    sa.Column('rax_left_total', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('leagues',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('pd_link', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('tier', sa.Integer(), nullable=True),
                    sa.Column('start_date', sa.Integer(), nullable=True),
                    sa.Column('end_date', sa.Integer(), nullable=True),
                    sa.Column('has_dates', sa.Boolean(), nullable=False),
                    sa.Column('has_started', sa.Boolean(), nullable=True),
                    sa.Column('has_ended', sa.Boolean(), nullable=True),
                    sa.Column('fully_parsed', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('performance_data_categories',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('players',
                    sa.Column('steam_id', sa.BIGINT(), nullable=True),
                    sa.Column('nickname', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('account_id', sa.Integer(), nullable=False),
                    sa.Column('official_name', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('account_id'),
                    sa.UniqueConstraint('steam_id')
                    )
    op.create_table('positions',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('teams',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('tag', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('buildings_data',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('dire', sa.Boolean(), nullable=False),
                    sa.Column('destroyed_buildings', sa.Integer(), nullable=True),
                    sa.Column('destroyed_towers', sa.Integer(), nullable=True),
                    sa.Column('destroyed_rax', sa.Integer(), nullable=True),
                    sa.Column('destroyed_lane_1', sa.Boolean(), nullable=False),
                    sa.Column('destroyed_lane_2', sa.Boolean(), nullable=False),
                    sa.Column('destroyed_lane_3', sa.Boolean(), nullable=False),
                    sa.Column('megacreeps', sa.Boolean(), nullable=True),
                    sa.Column('naked_throne', sa.Boolean(), nullable=True),
                    sa.Column('not_destroyed_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['not_destroyed_id'], ['in_game_buildings_not_destroyed.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('comparison_types',
                    sa.Column('player_cpd_id', sa.Integer(), nullable=True),
                    sa.Column('player_cps_id', sa.Integer(), nullable=True),
                    sa.Column('hero_cpd_id', sa.Integer(), nullable=True),
                    sa.Column('hero_cps_id', sa.Integer(), nullable=True),
                    sa.Column('pos_cpd_id', sa.Integer(), nullable=True),
                    sa.Column('pos_cps_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('flat', sa.Boolean(), nullable=False),
                    sa.Column('general', sa.Boolean(), nullable=False),
                    sa.ForeignKeyConstraint(['hero_cpd_id'], ['heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['hero_cps_id'], ['heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['player_cpd_id'], ['players.account_id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['player_cps_id'], ['players.account_id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['pos_cpd_id'], ['positions.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['pos_cps_id'], ['positions.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('data_aggregation_types',
                    sa.Column('player_id', sa.Integer(), nullable=True),
                    sa.Column('hero_id', sa.Integer(), nullable=True),
                    sa.Column('position_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('league_id', sa.Integer(), nullable=True),
                    sa.Column('by_player', sa.Boolean(), nullable=False),
                    sa.Column('by_hero', sa.Boolean(), nullable=False),
                    sa.Column('by_hero_pos_spec', sa.Integer(), nullable=True),
                    sa.Column('by_position', sa.Boolean(), nullable=False),
                    sa.ForeignKeyConstraint(['hero_id'], ['heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
                    sa.ForeignKeyConstraint(['player_id'], ['players.account_id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('performance_data_types',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('is_comparable', sa.Boolean(), nullable=True),
                    sa.Column('system_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('data_category_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['data_category_id'], ['performance_data_categories.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('games',
                    sa.Column('id', sa.BIGINT(), nullable=False),
                    sa.Column('sent_team_id', sa.Integer(), nullable=True),
                    sa.Column('dire_team_id', sa.Integer(), nullable=True),
                    sa.Column('game_start_time', sa.BIGINT(), nullable=False),
                    sa.Column('league_id', sa.Integer(), nullable=True),
                    sa.Column('dire_win', sa.Boolean(), nullable=False),
                    sa.Column('average_roshan_window_time', sa.Integer(), nullable=True),
                    sa.Column('first_ten_kills_dire', sa.Boolean(), nullable=False),
                    sa.Column('dire_lost_first_tower', sa.Boolean(), nullable=False),
                    sa.Column('dire_building_status_id', sa.Integer(), nullable=True),
                    sa.Column('sent_building_status_id', sa.Integer(), nullable=True),
                    sa.Column('duration', sa.Integer(), nullable=False),
                    sa.Column('replay_url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.ForeignKeyConstraint(['dire_building_status_id'], ['buildings_data.id'], ),
                    sa.ForeignKeyConstraint(['dire_team_id'], ['teams.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
                    sa.ForeignKeyConstraint(['sent_building_status_id'], ['buildings_data.id'], ),
                    sa.ForeignKeyConstraint(['sent_team_id'], ['teams.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('in_game_buildings_destroyed',
                    sa.Column('building_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('death_time', sa.Integer(), nullable=False),
                    sa.Column('destruction_order', sa.Integer(), nullable=True),
                    sa.Column('destruction_order_tower', sa.Integer(), nullable=True),
                    sa.Column('destruction_order_rax', sa.Integer(), nullable=True),
                    sa.Column('destroyed_lane_1', sa.Boolean(), nullable=False),
                    sa.Column('destroyed_lane_2', sa.Boolean(), nullable=False),
                    sa.Column('destroyed_lane_3', sa.Boolean(), nullable=False),
                    sa.Column('megacreeps', sa.Boolean(), nullable=False),
                    sa.Column('naked_throne', sa.Boolean(), nullable=False),
                    sa.Column('building_data_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['building_data_id'], ['buildings_data.id'], ),
                    sa.ForeignKeyConstraint(['building_id'], ['in_game_buildings.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('hero_deaths',
                    sa.Column('killer_hero_id', sa.Integer(), nullable=True),
                    sa.Column('killer_player_id', sa.Integer(), nullable=True),
                    sa.Column('victim_hero_id', sa.Integer(), nullable=True),
                    sa.Column('victim_player_id', sa.Integer(), nullable=True),
                    sa.Column('game_id', sa.BIGINT(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('death_number', sa.Integer(), nullable=False),
                    sa.Column('death_time', sa.Integer(), nullable=False),
                    sa.Column('kill_dire', sa.Boolean(), nullable=True),
                    sa.Column('victim_dire', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['killer_hero_id'], ['heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['killer_player_id'], ['players.account_id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['victim_hero_id'], ['heroes.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['victim_player_id'], ['players.account_id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('players_game_data',
                    sa.Column('game_id', sa.BIGINT(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('team_id', sa.Integer(), nullable=True),
                    sa.Column('player_id', sa.Integer(), nullable=True),
                    sa.Column('position_id', sa.Integer(), nullable=True),
                    sa.Column('hero_id', sa.Integer(), nullable=True),
                    sa.Column('slot', sa.Integer(), nullable=False),
                    sa.Column('lane', sa.Integer(), nullable=False),
                    sa.Column('is_roaming', sa.Boolean(), nullable=False),
                    sa.Column('win', sa.Boolean(), nullable=False),
                    sa.Column('dire', sa.Boolean(), nullable=False),
                    sa.Column('rank', sa.Integer(), nullable=True),
                    sa.Column('apm', sa.Integer(), nullable=False),
                    sa.Column('pings', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
                    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['hero_id'], ['heroes.id'], ),
                    sa.ForeignKeyConstraint(['player_id'], ['players.account_id'], ),
                    sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
                    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('roshan_deaths',
                    sa.Column('game_id', sa.BIGINT(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('death_number', sa.Integer(), nullable=False),
                    sa.Column('death_time', sa.Integer(), nullable=False),
                    sa.Column('kill_dire', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('games_performance',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('is_comparison', sa.Boolean(), nullable=False),
                    sa.Column('comparison_id', sa.Integer(), nullable=True),
                    sa.Column('is_aggregation', sa.Boolean(), nullable=False),
                    sa.Column('aggregation_id', sa.Integer(), nullable=True),
                    sa.Column('player_game_data_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['aggregation_id'], ['data_aggregation_types.id'], ),
                    sa.ForeignKeyConstraint(['comparison_id'], ['comparison_types.id'], ),
                    sa.ForeignKeyConstraint(['player_game_data_id'], ['players_game_data.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('performance_totals_data',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('total_gold', sa.Integer(), nullable=False),
                    sa.Column('total_xp', sa.Integer(), nullable=False),
                    sa.Column('kills_per_min', sa.Numeric(precision=10, scale=2), nullable=False),
                    sa.Column('kda', sa.Numeric(precision=5, scale=2), nullable=False),
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
                    sa.Column('first_blood_claimed', sa.Numeric(precision=5, scale=2), nullable=True),
                    sa.Column('first_kill_time', sa.Integer(), nullable=True),
                    sa.Column('died_first', sa.Numeric(precision=5, scale=2), nullable=True),
                    sa.Column('first_death_time', sa.Integer(), nullable=True),
                    sa.Column('lost_tower_first', sa.Numeric(precision=5, scale=2), nullable=True),
                    sa.Column('lost_tower_lane', sa.Integer(), nullable=True),
                    sa.Column('lost_tower_time', sa.Integer(), nullable=True),
                    sa.Column('destroyed_tower_first', sa.Numeric(precision=5, scale=2), nullable=True),
                    sa.Column('destroyed_tower_lane', sa.Integer(), nullable=True),
                    sa.Column('destroyed_tower_time', sa.Integer(), nullable=True),
                    sa.Column('game_performance_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['game_performance_id'], ['games_performance.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('performance_windows_data',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('data_type_id', sa.Integer(), nullable=True),
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
                    sa.ForeignKeyConstraint(['data_type_id'], ['performance_data_types.id'], ),
                    sa.ForeignKeyConstraint(['game_performance_id'], ['games_performance.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('performance_windows_data')
    op.drop_table('performance_totals_data')
    op.drop_table('games_performance')
    op.drop_table('roshan_deaths')
    op.drop_table('players_game_data')
    op.drop_table('hero_deaths')
    op.drop_table('in_game_buildings_destroyed')
    op.drop_table('games')
    op.drop_table('performance_data_types')
    op.drop_table('data_aggregation_types')
    op.drop_table('comparison_types')
    op.drop_table('buildings_data')
    op.drop_table('teams')
    op.drop_table('positions')
    op.drop_table('players')
    op.drop_table('performance_data_categories')
    op.drop_table('leagues')
    op.drop_table('in_game_buildings_not_destroyed')
    op.drop_table('in_game_buildings')
    op.drop_index(op.f('ix_heroes_name'), table_name='heroes')
    op.drop_table('heroes')
    # ### end Alembic commands ###