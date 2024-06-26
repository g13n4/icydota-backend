"""positions_cross

Revision ID: 14552906d445
Revises: 3a5491d5b572
Create Date: 2024-03-15 20:55:30.060335

"""
from typing import Sequence, Union

from db import SQLModel
import sqlmodel.sql.sqltypes

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14552906d445'
down_revision: Union[str, None] = '3a5491d5b572'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('data_aggregation_types', sa.Column('sup_cross', sa.Boolean(), nullable=True))
    op.add_column('data_aggregation_types', sa.Column('carry_cross', sa.Boolean(), nullable=True))
    op.add_column('data_aggregation_types', sa.Column('mid_cross', sa.Boolean(), nullable=True))
    op.add_column('leagues', sa.Column('parsed_before', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('leagues', 'parsed_before')
    op.drop_column('data_aggregation_types', 'mid_cross')
    op.drop_column('data_aggregation_types', 'carry_cross')
    op.drop_column('data_aggregation_types', 'sup_cross')
    # ### end Alembic commands ###
