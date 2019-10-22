"""add participant summary last modified

Revision ID: adb4ea532f1a
Revises: e4518d7d1af1
Create Date: 2018-03-08 13:23:40.782964

"""
import model.utils
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "adb4ea532f1a"
down_revision = "e4518d7d1af1"
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


def upgrade_rdr():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("participant_summary", sa.Column("last_modified", model.utils.UTCDateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade_rdr():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("participant_summary", "last_modified")
    # ### end Alembic commands ###


def upgrade_metrics():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_metrics():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###