"""created_at_for_aggregation

Revision ID: 51628b363f79
Revises: ce44ca879dc2
Create Date: 2024-02-20 22:26:27.254707

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '51628b363f79'
down_revision: Union[str, None] = 'ce44ca879dc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('data_aggregation_types', sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))


def downgrade() -> None:
    op.drop_column('data_aggregation_types', 'created_at')
