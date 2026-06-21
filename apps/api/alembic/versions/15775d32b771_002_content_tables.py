"""002_content_tables

Revision ID: 15775d32b771
Revises: 0dcad361c805
Create Date: ...
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

revision = "15775d32b771"
down_revision = "0dcad361c805" # id file 1
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Table: folders
    op.create_table(
        "folders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("owner_id", "name", name="uq_folder_name_per_user"),
    )
    op.create_index("idx_folders_owner", "folders", ["owner_id"])
    op.execute("""
        CREATE TRIGGER trg_folders_updated_at
            BEFORE UPDATE ON folders
            FOR EACH ROW EXECUTE FUNCTION set_updated_at()
    """)

    # Table: study_sets
    op.create_table(
        "study_sets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("folder_id", UUID(as_uuid=True), sa.ForeignKey("folders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("tags", ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("is_public", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("card_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("cloned_from", UUID(as_uuid=True), sa.ForeignKey("study_sets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_sets_owner", "study_sets", ["owner_id"])
    op.create_index("idx_sets_owner_folder", "study_sets", ["owner_id", "folder_id"])
    op.create_index("idx_sets_cloned_from", "study_sets", ["cloned_from"])
    op.create_index(
        "idx_sets_tags_gin", "study_sets", ["tags"],
        postgresql_using="gin"
    )
    op.create_index(
        "idx_sets_public_tags", "study_sets", ["is_public", "tags"],
        postgresql_where=sa.text("is_public = TRUE")
    )
    op.execute("""
        CREATE TRIGGER trg_sets_updated_at
            BEFORE UPDATE ON study_sets
            FOR EACH ROW EXECUTE FUNCTION set_updated_at()
    """)

    # FTS vector cho study_sets
    op.execute("""
        ALTER TABLE study_sets ADD COLUMN fts_vector TSVECTOR
            GENERATED ALWAYS AS (
                setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(description, '')), 'B')
            ) STORED
    """)
    op.execute("""
        CREATE INDEX idx_sets_fts ON study_sets USING GIN (fts_vector)
    """)

    # Table: cards
    op.create_table(
        "cards",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("study_set_id", UUID(as_uuid=True), sa.ForeignKey("study_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("front", sa.Text, nullable=False),
        sa.Column("back", sa.Text, nullable=False),
        sa.Column("image_url", sa.Text, nullable=True),
        sa.Column("order", sa.Float, nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_cards_set_order", "cards", ["study_set_id", "order"])
    op.create_index("idx_cards_owner", "cards", ["owner_id"])
    op.execute("""
        CREATE TRIGGER trg_cards_updated_at
            BEFORE UPDATE ON cards
            FOR EACH ROW EXECUTE FUNCTION set_updated_at()
    """)

    # Trigger: tự động cập nhật card_count trong study_sets
    op.execute("""
        CREATE OR REPLACE FUNCTION update_card_count()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                UPDATE study_sets SET card_count = card_count + 1 WHERE id = NEW.study_set_id;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE study_sets SET card_count = card_count - 1 WHERE id = OLD.study_set_id;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql
    """)
    op.execute("""
        CREATE TRIGGER trg_card_count
            AFTER INSERT OR DELETE ON cards
            FOR EACH ROW EXECUTE FUNCTION update_card_count()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_card_count ON cards")
    op.execute("DROP FUNCTION IF EXISTS update_card_count()")
    op.execute("DROP TRIGGER IF EXISTS trg_cards_updated_at ON cards")
    op.execute("DROP TRIGGER IF EXISTS trg_sets_updated_at ON study_sets")
    op.execute("DROP TRIGGER IF EXISTS trg_folders_updated_at ON folders")
    op.drop_table("cards")
    op.drop_table("study_sets")
    op.drop_table("folders")
