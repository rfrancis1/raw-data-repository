#! /bin/env python
#
# Copy Consent EHR files to HPO buckets.
#
# Replaces older ehr_upload_for_organization.sh script.
#

import io
import argparse

# pylint: disable=superfluous-parens
# pylint: disable=broad-except
import csv
import json
import logging
import os
import random
import sys
import tempfile
from datetime import datetime

import MySQLdb
import pytz

from rdr_service.storage import GoogleCloudStorageProvider
from rdr_service.services.gcp_utils import gcp_cp, gcp_format_sql_instance, gcp_make_auth_header
from rdr_service.services.system_utils import make_api_request, print_progress_bar, setup_logging, setup_i18n
from rdr_service.tools.tool_libs import GCPProcessContext

_logger = logging.getLogger("rdr_logger")

# Tool_cmd and tool_desc name are required.
# Remember to add/update bash completion in 'tool_lib/tools.bash'
tool_cmd = "sync-consents"
tool_desc = "manually sync consent files to sites"

HPO_REPORT_CONFIG_GCS_PATH = "gs://all-of-us-rdr-sequestered-config-test/hpo-report-config-mixin.json"
SOURCE_BUCKET = {
    "vibrent": "gs://ptc-uploads-all-of-us-rdr-prod/Participant/P{p_id}/*{file_ext}",
    "careevolution": "gs://ce-uploads-all-of-us-rdr-prod/Participant/P{p_id}/*{file_ext}"
}
DEST_BUCKET = "gs://{bucket_name}/Participant/{org_external_id}/{site_name}/P{p_id}/"

PARTICIPANT_SQL = """
select participant.participant_id,
       participant.participant_origin,
       site.google_group,
       organization.external_id
from participant
         left join organization
                   on participant.organization_id = organization.organization_id
         left join site
                   on participant.site_id = site.site_id
         left join participant_summary summary
                   on participant.participant_id = summary.participant_id
where TRUE
  and summary.consent_for_study_enrollment = 1
  and participant.is_ghost_id is not true
  and (
        summary.email is null
        or summary.email not like '@example.com'
    )
"""

participant_filters_sql = {
    'org_id_sql': 'and organization.external_id = "{org_id}" ',
    'date_limit_sql': """
        and ( 
            summary.consent_for_study_enrollment_time > "{date_limit}"
            or
            summary.consent_for_electronic_health_records_time > "{date_limit}"
            )            
        """,
    'end_date_sql': """
        and ( 
            summary.consent_for_study_enrollment_time < "{end_date}"
            or
            summary.consent_for_electronic_health_records_time < "{end_date}"
            ) 
        """,
}

COUNT_SQL = "select count(1) {0}".format(PARTICIPANT_SQL[PARTICIPANT_SQL.find("from") :])

class SyncConsentClass(object):
    def __init__(self, args, gcp_env):
        self.args = args
        self.gcp_env = gcp_env

        self.sql = PARTICIPANT_SQL
        self.count_sql = str()

        self.file_filter = ".pdf"

    def _format_count_sql(self):
        self.count_sql = "select count(1) {0}".format(self.sql[self.sql.find("from") :])

    def _add_participant_filter(self, filter_key, **kwargs):
        self.sql += participant_filters_sql[filter_key].format(**kwargs)

    def _get_files_updated_in_range(self, source_bucket, date_limit, p_id):
        """
        Uses the date limit to filter cloud storage files by the date
        :param source_bucket:
        :param date_limit:
        :param p_id:
        :return:
        """
        directory = source_bucket.split('/')[2]
        timezone = pytz.timezone('Etc/Greenwich')
        date_limit_obj = timezone.localize(datetime.strptime(date_limit, '%Y-%m-%d'))
        prefix = f'Participant/P{p_id}'
        try:
            provider = GoogleCloudStorageProvider()
            files = list(provider.list(directory, prefix=prefix))
            file_list = [
                f.name.replace(f'{prefix}', f'gs://{directory}/{prefix}')
                for f in files if f.updated > date_limit_obj
                and f.name.endswith(self.file_filter)
            ]
            return file_list
        except FileNotFoundError:
            return False

    def _format_debug_out(self, p_id, src, dest):
        _logger.debug(" Participant: {0}".format(p_id))
        _logger.debug("    src: {0}".format(src))
        _logger.debug("   dest: {0}".format(dest))

    def run(self):
        """
    Main program process
    :return: Exit code value
    """
        # TODO: Future: these two blocks of code should be replaced by Tanner's new config bucket for sites csv files.
        # Copy the bucket config file to a temp file
        _logger.info("retrieving configuration...")
        tmpfile = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()))
        gcp_cp(HPO_REPORT_CONFIG_GCS_PATH, tmpfile)
        # Read the tempfile and get the sheet_id from it.
        config = json.loads(open(tmpfile).read())
        sheet_id = config.get("hpo_report_google_sheet_id")
        # delete tempfile
        os.remove(tmpfile)

        # download the sheet in csv format
        _logger.info("retrieving sites config...")
        sheet_url = "spreadsheets/d/{0}/export?format=csv".format(sheet_id)
        resp_code, resp_data = make_api_request("docs.google.com", sheet_url, ret_type="text")
        if resp_code != 200:
            _logger.error(resp_data)
            _logger.error("failed to retrieve site information, aborting.")
            return 1
        # TODO end

        # Load the site info we need into a dict.
        sites = dict()
        handle = io.StringIO(resp_data)
        sites_reader = csv.DictReader(handle)
        for row in sites_reader:
            if row["Org ID"]:
                sites[row["Org ID"]] = {
                    "aggregating_org_id": row["Aggregating Org ID"],
                    "bucket_name": row["Bucket Name"],
                }

        _logger.info("retrieving db configuration...")
        headers = gcp_make_auth_header()
        resp_code, resp_data = make_api_request(
            "{0}.appspot.com".format(self.gcp_env.project), "/rdr/v1/Config/db_config", headers=headers
        )
        if resp_code != 200:
            _logger.error(resp_data)
            _logger.error("failed to retrieve config, aborting.")
            return 1

        passwd = resp_data["rdr_db_password"]
        if not passwd:
            _logger.error("failed to retrieve database user password from config.")
            return 1

        # connect a sql proxy to the current project
        _logger.info("starting google sql proxy...")
        port = random.randint(10000, 65535)
        instances = gcp_format_sql_instance(self.gcp_env.project, port=port)
        proxy_pid = self.gcp_env.activate_sql_proxy(instance=instances, port=port)
        if not proxy_pid:
            _logger.error("activating google sql proxy failed.")
            return 1

        try:
            _logger.info("connecting to mysql instance...")
            sql_conn = MySQLdb.connect(host="127.0.0.1", user="rdr", passwd=str(passwd), db="rdr", port=port)
            cursor = sql_conn.cursor()

            _logger.info("retrieving participant information...")
            # get record count
            if self.args.date_limit:
                # TODO: Add execption handling for incorrect date format
                self._add_participant_filter('date_limit_sql',
                                             date_limit=self.args.date_limit)
            if self.args.end_date:
                # TODO: Add execption handling for incorrect date format
                self._add_participant_filter('end_date_sql',
                                             end_date=self.args.end_date)

            if self.args.org_id:
                self._add_participant_filter('org_id_sql',
                                             org_id=self.args.org_id)
            self._format_count_sql()
            cursor.execute(self.count_sql)
            rec = cursor.fetchone()
            total_recs = rec[0]

            cursor.execute(self.sql)

            _logger.info("transferring files to destinations...")
            count = 0
            rec = cursor.fetchone()
            while rec:
                if not self.args.debug:
                    print_progress_bar(
                        count, total_recs, prefix="{0}/{1}:".format(count, total_recs), suffix="complete"
                    )

                p_id = rec[0]
                origin_id = rec[1]
                site = rec[2]
                if self.args.destination_bucket is not None:
                    # override destination bucket lookup (the lookup table is incomplete)
                    bucket = self.args.destination_bucket
                else:
                    site_info = sites.get(rec[3])
                    if not site_info:
                        _logger.warning("\nsite info not found for [{0}].".format(rec[2]))
                        count += 1
                        rec = cursor.fetchone()
                        continue
                    bucket = site_info.get("bucket_name")
                if not bucket:
                    _logger.warning("\nno bucket name found for [{0}].".format(rec[2]))
                    count += 1
                    rec = cursor.fetchone()
                    continue

                # Copy all files, not just PDFs
                if self.args.all_files:
                    self.file_filter = ""

                src_bucket = SOURCE_BUCKET.get(origin_id, SOURCE_BUCKET[
                    next(iter(SOURCE_BUCKET))
                ]).format(p_id=p_id, file_ext=self.file_filter)

                dest_bucket = DEST_BUCKET.format(
                    bucket_name=bucket,
                    org_external_id=self.args.org_id,
                    site_name=site if site else "no-site-assigned",
                    p_id=p_id,
                )
                if self.args.date_limit:
                    # only copy files newer than date limit
                    files_in_range = self._get_files_updated_in_range(
                        date_limit=self.args.date_limit,
                        source_bucket=src_bucket, p_id=p_id)
                    if not files_in_range or len(files_in_range) == 0:
                        _logger.info(f'No files in bucket updated after {self.args.date_limit}')
                    for f in files_in_range:
                        if not self.args.dry_run:
                            # actually copy the fles
                            gcp_cp(f, dest_bucket, args="-r", flags="-m")

                        self._format_debug_out(p_id, f, dest_bucket)

                else:
                    if not self.args.dry_run:
                        gcp_cp(src_bucket, dest_bucket, args="-r", flags="-m")

                    self._format_debug_out(p_id, src_bucket, dest_bucket)

                count += 1
                rec = cursor.fetchone()

            # print progressbar one more time to show completed.
            if not rec and not self.args.debug:
                print_progress_bar(
                    count, total_recs, prefix="{0}/{1}:".format(count, total_recs), suffix="complete"
                )

            cursor.close()
            sql_conn.close()

        except MySQLdb.OperationalError as e:
            _logger.error("failed to connect to {0} mysql instance. [{1}]".format(self.gcp_env.project, e))

        return 0


def run():
    # Set global debug value and setup application logging.
    setup_logging(
        _logger, tool_cmd, "--debug" in sys.argv, "{0}.log".format(tool_cmd) if "--log-file" in sys.argv else None
    )
    setup_i18n()

    # Setup program arguments.
    parser = argparse.ArgumentParser(prog=tool_cmd, description=tool_desc)
    parser.add_argument("--debug", help="Enable debug output", default=False, action="store_true")  # noqa
    parser.add_argument("--log-file", help="write output to a log file", default=False, action="store_true")  # noqa
    parser.add_argument("--project", help="gcp project name", default="localhost")  # noqa
    parser.add_argument("--account", help="pmi-ops account", default=None)  # noqa
    parser.add_argument("--service-account", help="gcp iam service account", default=None)  # noqa
    parser.add_argument("--org-id", help="organization id", default=None)  # noqa
    parser.add_argument(
        "--destination-bucket", default=None, help="Override the destination bucket lookup for the given organization."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Do not copy files, only print the list of files that would be copied"
    )

    parser.add_argument(
        "--date-limit", help="Limit consents to sync to those created after the date", default=None)  # noqa

    parser.add_argument(
        "--end-date", help="Limit consents to sync to those created before the date", default=None)  # noqa

    parser.add_argument(
        "--all-files", help="Transfer all file types, default is only PDF.",
        default=False, action="store_true")  # noqa

    args = parser.parse_args()

    with GCPProcessContext(tool_cmd, args.project, args.account, args.service_account) as gcp_env:
        process = SyncConsentClass(args, gcp_env)
        exit_code = process.run()
        return exit_code


# --- Main Program Call ---
if __name__ == "__main__":
    sys.exit(run())
