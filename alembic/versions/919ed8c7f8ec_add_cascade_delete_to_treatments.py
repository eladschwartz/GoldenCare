"""add_cascade_delete_to_treatments

Revision ID: 919ed8c7f8ec
Revises: b0a16991ef38
Create Date: 2024-12-27 15:50:56.675392

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '919ed8c7f8ec'
down_revision: Union[str, None] = 'b0a16991ef38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
