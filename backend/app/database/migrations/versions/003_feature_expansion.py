"""Feature expansion: sentiment, chat, schedules, diffs, onepager, financials

revision = "003_feature_expansion"
down_revision = "000_initial"
Create Date: 2026-10-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "003_feature_expansion"
down_revision = "000_initial"# adjust if you have previous migrations
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── reports: new columns ──────────────────────────────────
    op.add_column("reports", sa.Column("previous_report_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("reports", sa.Column("sentiment_summary", postgresql.JSONB, nullable=True))
    op.add_column("reports", sa.Column("financial_summary", postgresql.JSONB, nullable=True))
    op.add_column("reports", sa.Column("onepager", postgresql.JSONB, nullable=True))
    op.add_column("reports", sa.Column("diff_significance", sa.Integer, nullable=True))

    op.create_foreign_key(
        "fk_reports_previous_report_id",
        "reports", "reports",
        ["previous_report_id"], ["id"],
        ondelete="SET NULL",
    )

    # ─── sentiment_records ─────────────────────────────────────
    op.create_table(
        "sentiment_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("research_requests.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("company", sa.String(255), nullable=False, index=True),
        sa.Column("score", sa.Float, nullable=False, server_default="0"),
        sa.Column("label", sa.String(20), nullable=False, server_default="neutral"),
        sa.Column("distribution", postgresql.JSONB, nullable=True),
        sa.Column("drivers", postgresql.JSONB, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("articles", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── chat_conversations ────────────────────────────────────
    op.create_table(
        "chat_conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── chat_messages ─────────────────────────────────────────
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("sources", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── research_schedules ────────────────────────────────────
    op.create_table(
        "research_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("industry", sa.String(255), nullable=True),
        sa.Column("research_depth", sa.String(50), nullable=False, server_default="standard"),
        sa.Column("frequency", sa.String(50), nullable=False, server_default="weekly"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("last_run_at", sa.String(50), nullable=True),
        sa.Column("next_run_at", sa.String(50), nullable=True),
        sa.Column("runs_completed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── report_diffs ──────────────────────────────────────────
    op.create_table(
        "report_diffs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("current_report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("previous_report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("research_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("significance", sa.Integer, nullable=False, server_default="0"),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("payload", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── financial_profiles ────────────────────────────────────
    op.create_table(
        "financial_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("research_requests.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("company", sa.String(255), nullable=False, index=True),
        sa.Column("total_raised", sa.String(100), nullable=True),
        sa.Column("total_raised_millions", sa.Float, nullable=True),
        sa.Column("latest_valuation", sa.String(100), nullable=True),
        sa.Column("estimated_revenue", sa.String(100), nullable=True),
        sa.Column("investors", postgresql.JSONB, nullable=True),
        sa.Column("financial_signals", postgresql.JSONB, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── funding_rounds ────────────────────────────────────────
    op.create_table(
        "funding_rounds",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("financial_profiles.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("round_name", sa.String(100), nullable=True),
        sa.Column("amount", sa.String(100), nullable=True),
        sa.Column("amount_usd_millions", sa.Float, nullable=True),
        sa.Column("round_date", sa.String(50), nullable=True),
        sa.Column("lead_investor", sa.String(255), nullable=True),
        sa.Column("investors", postgresql.JSONB, nullable=True),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── investors ─────────────────────────────────────────────
    op.create_table(
        "investors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("financial_profiles.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("investors")
    op.drop_table("funding_rounds")
    op.drop_table("financial_profiles")
    op.drop_table("report_diffs")
    op.drop_table("research_schedules")
    op.drop_table("chat_messages")
    op.drop_table("chat_conversations")
    op.drop_table("sentiment_records")
    op.drop_constraint("fk_reports_previous_report_id", "reports", type_="foreignkey")
    op.drop_column("reports", "diff_significance")
    op.drop_column("reports", "onepager")
    op.drop_column("reports", "financial_summary")
    op.drop_column("reports", "sentiment_summary")
    op.drop_column("reports", "previous_report_id")