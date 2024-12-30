"""add name to patients table

Revision ID: 78567f8c3158
Revises: c9d81bea3e48
Create Date: 2024-12-23 12:53:33.594531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78567f8c3158'
down_revision: Union[str, None] = 'c9d81bea3e48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patients', sa.Column('name', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('patients', 'name')
    # ### end Alembic commands ###
