"""empty message

Revision ID: 6444d0542f22
Revises: e9e84e2c11e3
Create Date: 2024-08-27 09:07:39.848800

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6444d0542f22'
down_revision = 'e9e84e2c11e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('address',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('country', sa.String(length=100), nullable=False),
    sa.Column('state', sa.String(length=50), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=False),
    sa.Column('postal_code', sa.String(length=30), nullable=False),
    sa.Column('street', sa.String(length=100), nullable=True),
    sa.Column('house_number', sa.String(length=15), nullable=False),
    sa.Column('apartment_number', sa.String(length=10), nullable=True),
    sa.Column('company_id', sa.String(length=50), nullable=True),
    sa.Column('property_id', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], onupdate='cascade', ondelete='cascade'),
    sa.ForeignKeyConstraint(['property_id'], ['property.id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_address_id'), 'address', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_address_id'), table_name='address')
    op.drop_table('address')
    # ### end Alembic commands ###
