"""add_cascade_delete_to_treatments

Revision ID: 53b370f7bce9
Revises: 919ed8c7f8ec
Create Date: 2024-12-27 15:54:07.757419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53b370f7bce9'
down_revision: Union[str, None] = '919ed8c7f8ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
