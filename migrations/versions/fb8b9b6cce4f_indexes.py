"""indexes

Revision ID: fb8b9b6cce4f
Revises: 3422d2b88f6e
Create Date: 2024-03-02 17:18:18.100279

"""
from typing import Sequence, Union

from db import SQLModel
import sqlmodel.sql.sqltypes

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb8b9b6cce4f'
down_revision: Union[str, None] = '3422d2b88f6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_games_id'), 'games', ['id'], unique=False)
    op.create_index(op.f('ix_games_league_id'), 'games', ['league_id'], unique=False)
    op.create_index(op.f('ix_games_performance_aggregation_id'), 'games_performance', ['aggregation_id'], unique=False)
    op.create_index(op.f('ix_games_performance_comparison_id'), 'games_performance', ['comparison_id'], unique=False)
    op.create_index(op.f('ix_games_performance_is_aggregation'), 'games_performance', ['is_aggregation'], unique=False)
    op.create_index(op.f('ix_games_performance_is_comparison'), 'games_performance', ['is_comparison'], unique=False)
    op.create_index(op.f('ix_games_performance_player_game_data_id'), 'games_performance', [
        'player_game_data_id'], unique=False)
    op.create_index(op.f('ix_leagues_id'), 'leagues', ['id'], unique=False)
    op.create_index(op.f('ix_performance_data_types_data_category_id'), 'performance_data_types', [
        'data_category_id'], unique=False)
    op.create_index(op.f('ix_players_game_data_game_id'), 'players_game_data', ['game_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_players_game_data_game_id'), table_name='players_game_data')
    op.drop_index(op.f('ix_performance_data_types_data_category_id'), table_name='performance_data_types')
    op.drop_index(op.f('ix_leagues_id'), table_name='leagues')
    op.drop_index(op.f('ix_games_performance_player_game_data_id'), table_name='games_performance')
    op.drop_index(op.f('ix_games_performance_is_comparison'), table_name='games_performance')
    op.drop_index(op.f('ix_games_performance_is_aggregation'), table_name='games_performance')
    op.drop_index(op.f('ix_games_performance_comparison_id'), table_name='games_performance')
    op.drop_index(op.f('ix_games_performance_aggregation_id'), table_name='games_performance')
    op.drop_index(op.f('ix_games_league_id'), table_name='games')
    op.drop_index(op.f('ix_games_id'), table_name='games')
    # ### end Alembic commands ###
