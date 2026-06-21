"""004_system_config

Revision ID: e194d6a8698f
Revises: id_được_generate
Create Date: 2026-06-21 01:55:51.659952

"""
from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision: str = 'e194d6a8698f'
down_revision: Union[str, None] = 'id_được_generate'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "system_config",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("initial_ease_factor", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("min_ease_factor", sa.Float(), nullable=False, server_default="1.3"),
        sa.Column("known_threshold_days", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("max_sets_per_user", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("max_cards_per_set", sa.Integer(), nullable=False, server_default="500"),
        sa.Column("max_image_size_mb", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("allow_registration", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Insert duy nhất 1 row default (id=1) để app luôn có config sẵn dùng
    system_config_table = sa.table(
        "system_config",
        sa.column("id", sa.Integer()),
        sa.column("initial_ease_factor", sa.Float()),
        sa.column("min_ease_factor", sa.Float()),
        sa.column("known_threshold_days", sa.Integer()),
        sa.column("max_sets_per_user", sa.Integer()),
        sa.column("max_cards_per_set", sa.Integer()),
        sa.column("max_image_size_mb", sa.Integer()),
        sa.column("allow_registration", sa.Boolean()),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        system_config_table,
        [
            {
                "id": 1,
                "initial_ease_factor": 2.5,
                "min_ease_factor": 1.3,
                "known_threshold_days": 7,
                "max_sets_per_user": 50,
                "max_cards_per_set": 500,
                "max_image_size_mb": 5,
                "allow_registration": True,
                "updated_at": datetime.now(timezone.utc),
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("system_config")