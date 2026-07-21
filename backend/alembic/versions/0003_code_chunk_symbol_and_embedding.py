"""Add symbol_name and embedding columns to code_chunks."""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision = "0003_chunk_symbol_embedding"
down_revision = "0002_create_code_chunks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "code_chunks",
        sa.Column("symbol_name", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "code_chunks",
        sa.Column("embedding", Vector(1536), nullable=True),
    )
    op.add_column(
        "code_chunks",
        sa.Column("embedding_model", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "code_chunks",
        sa.Column("embedded_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("code_chunks", "embedded_at")
    op.drop_column("code_chunks", "embedding_model")
    op.drop_column("code_chunks", "embedding")
    op.drop_column("code_chunks", "symbol_name")
