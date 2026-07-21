"""Add code_chunks table."""

from alembic import op
import sqlalchemy as sa


revision = "0002_create_code_chunks"
down_revision = "0001_create_projects_and_files"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "code_chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=64), nullable=True),
        sa.Column("chunk_kind", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_code_chunks_project_id", "code_chunks", ["project_id"], unique=False)
    op.create_index("ix_code_chunks_file_id", "code_chunks", ["file_id"], unique=False)
    op.create_index(
        "ix_code_chunks_file_id_chunk_index",
        "code_chunks",
        ["file_id", "chunk_index"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_code_chunks_file_id_chunk_index", table_name="code_chunks")
    op.drop_index("ix_code_chunks_file_id", table_name="code_chunks")
    op.drop_index("ix_code_chunks_project_id", table_name="code_chunks")
    op.drop_table("code_chunks")
