"""Add optional semantic embedding vectors stored as JSON.

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("document_chunks", sa.Column("embedding", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("document_chunks", "embedding")
