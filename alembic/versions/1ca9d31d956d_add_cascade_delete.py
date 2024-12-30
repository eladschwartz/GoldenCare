"""add_cascade_delete

Revision ID: 1ca9d31d956d
Revises: 53b370f7bce9
Create Date: 2024-12-27 15:56:27.468229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ca9d31d956d'
down_revision: Union[str, None] = '53b370f7bce9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
