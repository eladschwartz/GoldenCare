"""add_cascade_delete

Revision ID: 873683dc9509
Revises: 1ca9d31d956d
Create Date: 2024-12-27 15:57:45.627325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '873683dc9509'
down_revision: Union[str, None] = '1ca9d31d956d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
