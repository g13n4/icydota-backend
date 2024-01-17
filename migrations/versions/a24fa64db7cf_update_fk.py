"""update_fk

Revision ID: a24fa64db7cf
Revises: d48b3758a7a4
Create Date: 2024-01-17 15:25:57.741544

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a24fa64db7cf'
down_revision: Union[str, None] = 'd48b3758a7a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('games_performance',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.drop_constraint('games_aggregated_by_hero_window_stats_id_fkey', 'games_aggregated_by_hero', type_='foreignkey')
    op.create_foreign_key(None, 'games_aggregated_by_hero', 'games_performance', ['window_stats_id'], ['id'])
    op.drop_constraint('games_aggregated_by_player_window_stats_id_fkey', 'games_aggregated_by_player',
                       type_='foreignkey')
    op.create_foreign_key(None, 'games_aggregated_by_player', 'games_performance', ['window_stats_id'], ['id'])
    op.drop_constraint('games_aggregated_by_position_window_stats_id_fkey', 'games_aggregated_by_position',
                       type_='foreignkey')
    op.create_foreign_key(None, 'games_aggregated_by_position', 'games_performance', ['window_stats_id'], ['id'])
    op.add_column('performance_totals_data', sa.Column('game_performance_id', sa.Integer(), nullable=True))
    op.drop_constraint('performance_totals_data_game_data_id_fkey', 'performance_totals_data', type_='foreignkey')
    op.create_foreign_key(None, 'performance_totals_data', 'games_performance', ['game_performance_id'], ['id'])
    op.drop_column('performance_totals_data', 'game_data_id')
    op.add_column('performance_windows_data', sa.Column('game_performance_id', sa.Integer(), nullable=True))
    op.drop_constraint('performance_windows_data_game_data_id_fkey', 'performance_windows_data', type_='foreignkey')
    op.create_foreign_key(None, 'performance_windows_data', 'games_performance', ['game_performance_id'], ['id'])
    op.drop_column('performance_windows_data', 'game_data_id')
    op.add_column('player_games_data', sa.Column('performance_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'player_games_data', 'games_performance', ['performance_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'player_games_data', type_='foreignkey')
    op.drop_column('player_games_data', 'performance_id')
    op.add_column('performance_windows_data',
                  sa.Column('game_data_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'performance_windows_data', type_='foreignkey')
    op.create_foreign_key('performance_windows_data_game_data_id_fkey', 'performance_windows_data', 'player_games_data',
                          ['game_data_id'], ['id'])
    op.drop_column('performance_windows_data', 'game_performance_id')
    op.add_column('performance_totals_data',
                  sa.Column('game_data_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'performance_totals_data', type_='foreignkey')
    op.create_foreign_key('performance_totals_data_game_data_id_fkey', 'performance_totals_data', 'player_games_data',
                          ['game_data_id'], ['id'])
    op.drop_column('performance_totals_data', 'game_performance_id')
    op.drop_constraint(None, 'games_aggregated_by_position', type_='foreignkey')
    op.create_foreign_key('games_aggregated_by_position_window_stats_id_fkey', 'games_aggregated_by_position',
                          'player_games_data', ['window_stats_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint(None, 'games_aggregated_by_player', type_='foreignkey')
    op.create_foreign_key('games_aggregated_by_player_window_stats_id_fkey', 'games_aggregated_by_player',
                          'player_games_data', ['window_stats_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint(None, 'games_aggregated_by_hero', type_='foreignkey')
    op.create_foreign_key('games_aggregated_by_hero_window_stats_id_fkey', 'games_aggregated_by_hero',
                          'player_games_data', ['window_stats_id'], ['id'], ondelete='SET NULL')
    op.drop_table('games_performance')
    # ### end Alembic commands ###
