"""patient status flag

Revision ID: 3c91f6fd0585
Revises: 397974e4d58d
Create Date: 2019-05-15 16:13:11.121942

"""
import model.utils
import sqlalchemy as sa
from alembic import op

from rdr_service.participant_enums import PatientStatusFlag

# revision identifiers, used by Alembic.
revision = "3c91f6fd0585"
down_revision = "397974e4d58d"
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


def upgrade_rdr():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "patient_status",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created", sa.DateTime(), nullable=True),
        sa.Column("modified", sa.DateTime(), nullable=True),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("patient_status", model.utils.Enum(PatientStatusFlag), nullable=False),
        sa.Column("hpo_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["hpo_id"], ["hpo.hpo_id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organization.organization_id"]),
        sa.ForeignKeyConstraint(["participant_id"], ["participant.participant_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("participant_id", "organization_id", name="uidx_patient_status"),
    )
    # ### end Alembic commands ###


def downgrade_rdr():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("patient_status")
    # ### end Alembic commands ###


def upgrade_metrics():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_metrics():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
