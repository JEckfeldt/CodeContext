"""Add HNSW index for cosine similarity search on code chunk embeddings."""

from alembic import op


revision = "0004_code_chunks_embedding_hnsw"
down_revision = "0003_chunk_symbol_embedding"
branch_labels = None
depends_on = None

HNSW_INDEX_NAME = "ix_code_chunks_embedding_hnsw"
VECTOR_COSINE_OPS = "vector_cosine_ops"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS {HNSW_INDEX_NAME}
        ON code_chunks
        USING hnsw (embedding {VECTOR_COSINE_OPS})
        WHERE embedding IS NOT NULL
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(f"DROP INDEX IF EXISTS {HNSW_INDEX_NAME}")
