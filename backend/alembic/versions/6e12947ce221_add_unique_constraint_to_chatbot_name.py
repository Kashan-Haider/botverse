from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint(
        'unique_chatbot_name',
        'chatbots',
        ['name']
    )


def downgrade():
    op.drop_constraint('unique_chatbot_name', 'chatbots', type_='unique')
