"""The main API definition file for endpoints that trigger MapReduces and batch tasks."""
import json
import logging
import time
import traceback
from datetime import datetime

from flask import Flask, request
from rdr_service.config import GAE_PROJECT
from sqlalchemy.exc import DBAPIError
from werkzeug.exceptions import BadRequest

from rdr_service import app_util, config
from rdr_service.api_util import EXPORTER
from rdr_service.dao.metric_set_dao import AggregateMetricsDao
from rdr_service.dao.metrics_dao import MetricsVersionDao
from rdr_service.offline import biobank_samples_pipeline, genomic_pipeline, sync_consent_files, update_ehr_status
from rdr_service.offline.base_pipeline import send_failure_alert
from rdr_service.offline.bigquery_sync import rebuild_bigquery_handler, sync_bigquery_handler
from rdr_service.offline.exclude_ghost_participants import mark_ghost_participants
from rdr_service.offline.metrics_export import MetricsExport
from rdr_service.offline.participant_counts_over_time import calculate_participant_metrics
from rdr_service.offline.participant_maint import skew_duplicate_last_modified
from rdr_service.offline.patient_status_backfill import backfill_patient_status
from rdr_service.offline.public_metrics_export import LIVE_METRIC_SET_ID, PublicMetricsExport
from rdr_service.offline.sa_key_remove import delete_service_account_keys
from rdr_service.offline.table_exporter import TableExporter

PREFIX = "/offline/"


def _alert_on_exceptions(func):
    """Sends e-mail alerts for any failure of the decorated function.

  This handles Biobank DataErrors specially.

  This must be the innermost (bottom) decorator in order to discover the wrapped function's name.
  """

    def alert_on_exceptions_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except biobank_samples_pipeline.DataError as e:
            # This is for CSVs older than 24h; we only want to send alerts in prod, where we expect
            # regular CSV uploads. In other environments, it's OK to just abort the CSV import if there's
            # no new data.
            biobank_recipients = config.getSettingList(config.BIOBANK_STATUS_MAIL_RECIPIENTS, default=[])
            if not e.external or (e.external and biobank_recipients):
                send_failure_alert(
                    func.__name__,
                    "Data error in Biobank samples pipeline: %s" % e,
                    log_exc_info=True,
                    extra_recipients=biobank_recipients,
                )
            else:
                # Don't alert for stale CSVs except in prod (where external recipients are configured).
                logging.info("Not alerting on external-only DataError (%s).", e)
            return json.dumps({"data_error": str(e)})
        except:
            send_failure_alert(func.__name__, "Exception in cron: %s" % traceback.format_exc())
            raise

    return alert_on_exceptions_wrapper


@app_util.auth_required_cron
@_alert_on_exceptions
def recalculate_metrics():
    in_progress = MetricsVersionDao().get_version_in_progress()
    if in_progress:
        logging.info("=========== Metrics pipeline already running ============")
        return '{"metrics-pipeline-status": "running"}'
    else:
        bucket_name = app_identity.get_default_gcs_bucket_name()
        logging.info("=========== Starting metrics export ============")
        MetricsExport.start_export_tasks(bucket_name, int(config.getSetting(config.METRICS_SHARDS, 1)))
        return '{"metrics-pipeline-status": "started"}'


@app_util.auth_required_cron
def recalculate_public_metrics():
    logging.info("generating public metrics")
    aggs = PublicMetricsExport.export(LIVE_METRIC_SET_ID)
    client_aggs = AggregateMetricsDao.to_client_json(aggs)

    # summing all counts for one metric yields a total qualified participant count
    participant_count = 0
    if len(client_aggs) > 0:
        participant_count = sum([a["count"] for a in client_aggs[0]["values"]])
    logging.info(
        "persisted public metrics: {} aggregations over " "{} participants".format(len(client_aggs), participant_count)
    )

    # Same format returned by the metric sets API.
    return json.dumps({"metrics": client_aggs})


@app_util.auth_required_cron
@_alert_on_exceptions
def import_biobank_samples():
    # Note that crons always have a 10 minute deadline instead of the normal 60s; additionally our
    # offline service uses basic scaling with has no deadline.
    logging.info("Starting samples import.")
    written, timestamp = biobank_samples_pipeline.upsert_from_latest_csv()
    logging.info("Import complete (%d written), generating report.", written)
    # waiting 30 secs for the replica DB synchronization
    time.sleep(30)
    logging.info("Generating reconciliation report.")
    # iterate new list and write reports
    biobank_samples_pipeline.write_reconciliation_report(timestamp)
    logging.info("Generated reconciliation report.")
    return json.dumps({"written": written})


@app_util.auth_required_cron
@_alert_on_exceptions
def biobank_monthly_reconciliation_report():
    # make sure this cron job is executed after import_biobank_samples
    timestamp = biobank_samples_pipeline.get_last_biobank_sample_file_info(monthly=True)[2]

    logging.info("Generating monthly reconciliation report.")
    # iterate new list and write reports
    biobank_samples_pipeline.write_reconciliation_report(timestamp, "monthly")
    logging.info("Generated monthly reconciliation report.")
    return json.dumps({"monthly-reconciliation-report": "generated"})


@app_util.auth_required(EXPORTER)
def export_tables():
    resource = request.get_data()
    resource_json = json.loads(resource)
    database = resource_json.get("database")
    tables = resource_json.get("tables")
    instance_name = resource_json.get("instance_name")
    if not database:
        raise BadRequest("database is required")
    if not tables or not isinstance(tables, list):
        raise BadRequest("tables is required")
    directory = resource_json.get("directory")
    if not directory:
        raise BadRequest("directory is required")

    # Ensure this has a boolean value to avoid downstream issues.
    deidentify = resource_json.get("deidentify") is True

    return json.dumps(TableExporter.export_tables(database, tables, directory, deidentify, instance_name))


@app_util.auth_required_cron
@_alert_on_exceptions
def skew_duplicates():
    skew_duplicate_last_modified()
    return '{"success": "true"}'


@app_util.auth_required_cron
@_alert_on_exceptions
def delete_old_keys():
    delete_service_account_keys()
    return '{"success": "true"}'


@app_util.auth_required_cron
@_alert_on_exceptions
def participant_counts_over_time():
    calculate_participant_metrics()
    return '{"success": "true"}'


@app_util.auth_required_cron
@_alert_on_exceptions
def exclude_ghosts():
    mark_ghost_participants()
    return '{"success": "true"}'


@app_util.auth_required_cron
@_alert_on_exceptions
def sync_consent_files():
    sync_consent_files.do_sync_consent_files()
    return '{"success": "true"}'


@app_util.auth_required_cron
@_alert_on_exceptions
def update_ehr_status():
    update_ehr_status.update_ehr_status()
    return '{"success": "true"}'


@app_util.auth_required_cron
@_alert_on_exceptions
def genomic_pipeline():
    genomic_pipeline.process_genomic_water_line()
    return '{"success": "true"}'


@app_util.auth_required_cron
@_alert_on_exceptions
def bigquery_rebuild_cron():
    """ this should always be a manually run job, but we have to schedule it at least once a year. """
    now = datetime.utcnow()
    if now.day == 0o1 and now.month == 0o1:
        logging.info("skipping the scheduled run.")
        return '{"success": "true"}'
    rebuild_bigquery_handler()
    return '{"success": "true"}'


@app_util.auth_required_cron
@_alert_on_exceptions
def bigquery_sync():
    sync_bigquery_handler()
    return '{"success": "true"}'


@app_util.auth_required_cron
@_alert_on_exceptions
def patient_status_backfill():
    # this should always be a manually run job, but we have to schedule it.
    now = datetime.utcnow()
    if now.day == 0o1 and now.month == 0o1:
        logging.info("skipping the scheduled run.")
        return '{"success": "true"}'
    backfill_patient_status()
    return '{"success": "true"}'


def _build_pipeline_app():
    """Configure and return the app with non-resource pipeline-triggering endpoints."""
    offline_app = Flask(__name__)

    offline_app.add_url_rule(
        PREFIX + "BiobankSamplesImport",
        endpoint="biobankSamplesImport",
        view_func=import_biobank_samples,
        methods=["GET"],
    )

    offline_app.add_url_rule(
        PREFIX + "MonthlyReconciliationReport",
        endpoint="monthlyReconciliationReport",
        view_func=biobank_monthly_reconciliation_report,
        methods=["GET"],
    )

    offline_app.add_url_rule(
        PREFIX + "SkewDuplicates", endpoint="skew_duplicates", view_func=skew_duplicates, methods=["GET"]
    )

    offline_app.add_url_rule(
        PREFIX + "MetricsRecalculate", endpoint="metrics_recalc", view_func=recalculate_metrics, methods=["GET"]
    )

    offline_app.add_url_rule(
        PREFIX + "PublicMetricsRecalculate",
        endpoint="public_metrics_recalc",
        view_func=recalculate_public_metrics,
        methods=["GET"],
    )

    offline_app.add_url_rule(
        PREFIX + "ExportTables", endpoint="ExportTables", view_func=export_tables, methods=["POST"]
    )

    offline_app.add_url_rule(
        PREFIX + "DeleteOldKeys", endpoint="delete_old_keys", view_func=delete_old_keys, methods=["GET"]
    )

    offline_app.add_url_rule(
        PREFIX + "ParticipantCountsOverTime",
        endpoint="participant_counts_over_time",
        view_func=participant_counts_over_time,
        methods=["GET"],
    )

    offline_app.add_url_rule(
        PREFIX + "MarkGhostParticipants", endpoint="exclude_ghosts", view_func=exclude_ghosts, methods=["GET"]
    )

    offline_app.add_url_rule(
        PREFIX + "SyncConsentFiles", endpoint="sync_consent_files", view_func=sync_consent_files, methods=["GET"]
    )

    offline_app.add_url_rule(
        PREFIX + "UpdateEhrStatus", endpoint="update_ehr_status", view_func=update_ehr_status, methods=["GET"]
    )

    offline_app.add_url_rule(
        PREFIX + "GenomicPipeline", endpoint="genomic_pipeline", view_func=genomic_pipeline, methods=["GET"]
    )

    offline_app.add_url_rule(
        PREFIX + "BigQueryRebuild", endpoint="bigquery_rebuild", view_func=bigquery_rebuild_cron, methods=["GET"]
    )

    offline_app.add_url_rule(
        PREFIX + "BigQuerySync", endpoint="bigquery_sync", view_func=bigquery_sync, methods=["GET"]
    )

    offline_app.add_url_rule(
        PREFIX + "PatientStatusBackfill",
        endpoint="patient_status_backfill",
        view_func=patient_status_backfill,
        methods=["GET"],
    )

    offline_app.after_request(app_util.add_headers)
    offline_app.before_request(app_util.request_logging)
    offline_app.register_error_handler(DBAPIError, app_util.handle_database_disconnect)

    return offline_app


app = _build_pipeline_app()