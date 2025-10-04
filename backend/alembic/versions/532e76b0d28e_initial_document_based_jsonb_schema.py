"""Initial document-based JSONB schema

Revision ID: 532e76b0d28e
Revises: 
Create Date: 2025-10-01 16:12:12.098280

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '532e76b0d28e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable UUID extension
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    
    # Users table
    op.execute("""
        CREATE TABLE users (
            _id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            document JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_users_email ON users USING BTREE ((document->>'email'))")
    
    # Visa Applications table
    op.execute("""
        CREATE TABLE visa_applications (
            _id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(_id) ON DELETE CASCADE,
            document JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_visa_applications_user_id ON visa_applications (user_id)")
    op.execute("CREATE INDEX idx_visa_applications_status ON visa_applications USING BTREE ((document->>'status'))")
    
    # Documents table
    op.execute("""
        CREATE TABLE documents (
            _id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(_id) ON DELETE CASCADE,
            application_id UUID REFERENCES visa_applications(_id) ON DELETE CASCADE,
            document JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_documents_user_id ON documents (user_id)")
    op.execute("CREATE INDEX idx_documents_application_id ON documents (application_id)")
    
    # Countries table
    op.execute("""
        CREATE TABLE countries (
            _id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            document JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_countries_code ON countries USING BTREE ((document->>'code'))")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS documents CASCADE")
    op.execute("DROP TABLE IF EXISTS visa_applications CASCADE") 
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TABLE IF EXISTS countries CASCADE")
