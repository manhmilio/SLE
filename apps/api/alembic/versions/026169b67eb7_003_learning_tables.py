"""003_learning_tables

Revision ID: 026169b67eb7
Revises: 15775d32b771
Create Date: 2026-05-29 14:23:15.325473

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

# revision identifiers, used by Alembic.
revision = "id_được_generate"
down_revision = "15775d32b771"   # ← id của 002
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Table: study_progress
    op.create_table(
        "study_progress",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("card_id", UUID(as_uuid=True), sa.ForeignKey("cards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_set_id", UUID(as_uuid=True), sa.ForeignKey("study_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("ease_factor", sa.Float, nullable=False, server_default=sa.text("2.5")),
        sa.Column("interval", sa.Integer, nullable=False, server_default=sa.text("1")),
        sa.Column("repetitions", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("next_review", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("last_reviewed", sa.DateTime(timezone=True), nullable=True),
        sa.Column("streak", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("user_id", "card_id", "mode", name="uq_progress_user_card_mode"),
        sa.CheckConstraint("mode IN ('flashcard', 'learn', 'test', 'match')", name="ck_progress_mode"),
    )
    op.create_index("idx_progress_user_card", "study_progress", ["user_id", "card_id"])
    op.create_index("idx_progress_next_review", "study_progress", ["user_id", "next_review"])
    op.create_index("idx_progress_set", "study_progress", ["user_id", "study_set_id"])
    op.execute("""
        CREATE TRIGGER trg_progress_updated_at
            BEFORE UPDATE ON study_progress
            FOR EACH ROW EXECUTE FUNCTION set_updated_at()
    """)

    # Table: study_sessions
    op.create_table(
        "study_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_set_id", UUID(as_uuid=True), sa.ForeignKey("study_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("cards_studied", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("correct", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("incorrect", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("mode IN ('flashcard', 'learn', 'test', 'match')", name="ck_session_mode"),
    )
    op.create_index(
        "idx_sessions_open", "study_sessions", ["user_id", "study_set_id", "mode"],
        postgresql_where=sa.text("ended_at IS NULL")
    )
    op.create_index(
        "idx_sessions_history", "study_sessions", ["user_id", sa.text("ended_at DESC")],
        postgresql_where=sa.text("ended_at IS NOT NULL")
    )
    op.create_index("idx_sessions_streak", "study_sessions", ["user_id", sa.text("created_at DESC")])

    # Table: session_answers
    op.create_table(
        "session_answers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", UUID(as_uuid=True), sa.ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("card_id", UUID(as_uuid=True), sa.ForeignKey("cards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("front", sa.Text, nullable=False),
        sa.Column("back", sa.Text, nullable=False),
        sa.Column("user_answer", sa.Text, nullable=True),
        sa.Column("quality", sa.SmallInteger, nullable=True),
        sa.Column("is_correct", sa.Boolean, nullable=False),
        sa.Column("time_spent", sa.Integer, nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("quality BETWEEN 1 AND 5", name="ck_answer_quality"),
    )
    op.create_index("idx_answers_session", "session_answers", ["session_id"])
    op.create_index("idx_answers_session_card", "session_answers", ["session_id", "card_id"])
    op.create_index("idx_answers_user_card", "session_answers", ["user_id", "card_id"])

    # Table: set_clones
    op.create_table(
        "set_clones",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("original_set_id", UUID(as_uuid=True), sa.ForeignKey("study_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_owner_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cloned_set_id", UUID(as_uuid=True), sa.ForeignKey("study_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cloned_by", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cloned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("original_set_id", "cloned_by", name="uq_clone"),
    )
    op.create_index("idx_clones_original", "set_clones", ["original_set_id"])
    op.create_index("idx_clones_by", "set_clones", ["cloned_by"])


def downgrade() -> None:
    op.drop_table("set_clones")
    op.drop_table("session_answers")
    op.drop_table("study_sessions")
    op.execute("DROP TRIGGER IF EXISTS trg_progress_updated_at ON study_progress")
    op.drop_table("study_progress")
