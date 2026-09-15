from alembic import op


# revision identifiers, used by Alembic.
revision = "afc6c1f3ed1b"
down_revision = "a65fbe87ac63"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # HNSW index for fast cosine-similarity vector search.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_chunks_embedding_hnsw
        ON chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )

    # PostgreSQL full-text search index for keyword retrieval.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_chunks_content_fts
        ON chunks
        USING gin (to_tsvector('english', content))
        """
    )

    # Useful metadata indexes for source filtering.
    op.create_index(
        "ix_chunks_guest",
        "chunks",
        ["guest"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_chunks_episode",
        "chunks",
        ["episode"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_chunks_episode",
        table_name="chunks",
    )

    op.drop_index(
        "ix_chunks_guest",
        table_name="chunks",
    )

    op.execute(
        "DROP INDEX IF EXISTS ix_chunks_content_fts"
    )

    op.execute(
        "DROP INDEX IF EXISTS ix_chunks_embedding_hnsw"
    )