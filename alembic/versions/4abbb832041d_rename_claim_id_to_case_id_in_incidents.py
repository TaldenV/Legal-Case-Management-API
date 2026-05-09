"""rename claim_id to case_id in incidents

Revision ID: 4abbb832041d
Revises: 277384581195
Create Date: 2026-05-09 04:05:35.256081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4abbb832041d'
down_revision: Union[str, None] = '277384581195'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('incidents', 'claim_id', new_column_name='case_id')


def downgrade() -> None:
    op.alter_column('incidents', 'case_id', new_column_name='claim_id')
