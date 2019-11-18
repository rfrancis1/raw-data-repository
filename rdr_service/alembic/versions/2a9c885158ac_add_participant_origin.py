"""add participant origin

Revision ID: 2a9c885158ac
Revises: bce6d443874f
Create Date: 2019-11-13 10:20:37.557338

"""
from alembic import op
import sqlalchemy as sa
import model.utils


from rdr_service.participant_enums import PhysicalMeasurementsStatus, QuestionnaireStatus, OrderStatus
from rdr_service.participant_enums import WithdrawalStatus, WithdrawalReason, SuspensionStatus, QuestionnaireDefinitionStatus
from rdr_service.participant_enums import EnrollmentStatus, Race, SampleStatus, OrganizationType, BiobankOrderStatus
from rdr_service.participant_enums import OrderShipmentTrackingStatus, OrderShipmentStatus
from rdr_service.participant_enums import MetricSetType, MetricsKey, GenderIdentity
from rdr_service.model.base import add_table_history_table, drop_table_history_table
from rdr_service.model.code import CodeType
from rdr_service.model.site_enums import SiteStatus, EnrollingStatus, DigitalSchedulingStatus, ObsoleteStatus

# revision identifiers, used by Alembic.
revision = '2a9c885158ac'
down_revision = 'bce6d443874f'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()



PARTICIPANT_ORIGIN = """update {0}
            set participant_origin =
            case when client_id like 'care%'
            then 'careevolution'
            else
            'vibrent'
            end
            where participant_id != 0;
            """

SUMMARY = """update participant_summary ps
                inner join participant p on ps.participant_id = p.participant_id
                set ps.participant_origin =
                        case when p.client_id like 'care%'
                                 then 'careevolution'
                             else
                                 'vibrent'
                            end
                where ps.participant_id != 0;
                """

def upgrade_rdr():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('participant', sa.Column('participant_origin', sa.String(length=80), nullable=False))
    op.add_column('participant_history', sa.Column('participant_origin', sa.String(length=80), nullable=False))
    op.add_column('participant_summary', sa.Column('participant_origin', sa.String(length=80), nullable=False))
    op.execute(PARTICIPANT_ORIGIN.format("participant"))
    op.execute(PARTICIPANT_ORIGIN.format("participant_history"))
    op.execute(SUMMARY)
    # ### end Alembic commands ###

def downgrade_rdr():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('participant_summary', 'participant_origin')
    op.drop_column('participant_history', 'participant_origin')
    op.drop_column('participant', 'participant_origin')
    # ### end Alembic commands ###


def upgrade_metrics():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_metrics():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
