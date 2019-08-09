"""patient status history

Revision ID: e5d456399216
Revises: 629f994cc809
Create Date: 2019-06-07 14:07:06.419651

"""
from alembic import op

from rdr_service.model.base import add_table_history_table, drop_table_history_table

# revision identifiers, used by Alembic.
revision = "e5d456399216"
down_revision = "629f994cc809"
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


def upgrade_rdr():
    # ### commands auto generated by Alembic - please adjust! ###
    add_table_history_table("patient_status", op)
    op.execute("""call sp_drop_index_if_exists('patient_status_history', 'uidx_patient_status')""")
    op.execute(
        """create index ix_participant_organization on rdr.patient_status_history (participant_id, organization_id)"""
    )
    # ### end Alembic commands ###


def downgrade_rdr():
    # ### commands auto generated by Alembic - please adjust! ###
    drop_table_history_table("patient_status", op)
    # ### end Alembic commands ###


def upgrade_metrics():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_metrics():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###