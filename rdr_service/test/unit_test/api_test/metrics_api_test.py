import datetime

from rdr_service.dao.metrics_dao import MetricsBucketDao, MetricsVersionDao
from rdr_service.model.metrics import MetricsBucket
from rdr_service.test.unit_test.unit_test_util import FlaskTestBase


# TODO: represent in new test suite
class MetricsApiTest(FlaskTestBase):
    def setUp(self):
        super(MetricsApiTest, self).setUp()
        self.version_dao = MetricsVersionDao()
        self.bucket_dao = MetricsBucketDao()
        self.today = datetime.date.today()
        self.tomorrow = self.today + datetime.timedelta(days=1)
        self.expected_bucket_1 = {"facets": {"date": self.today.isoformat()}, "entries": {"x": "a"}}
        self.expected_bucket_2 = {"facets": {"date": self.today.isoformat(), "hpoId": "PITT"}, "entries": {"x": "b"}}
        self.expected_bucket_3 = {"facets": {"date": self.tomorrow.isoformat()}, "entries": {"y": "c"}}

    def test_get_metrics_no_data(self):
        response = self.send_post(
            "Metrics", {"start_date": self.today.isoformat(), "end_date": self.tomorrow.isoformat()}
        )
        self.assertEqual([], response)

    def test_get_metrics_no_buckets(self):
        self.version_dao.set_pipeline_in_progress()
        self.version_dao.set_pipeline_finished(True)
        response = self.send_post(
            "Metrics", {"start_date": self.today.isoformat(), "end_date": self.tomorrow.isoformat()}
        )
        self.assertEqual([], response)

    def setup_buckets(self):
        self.version_dao.set_pipeline_in_progress()
        metrics_bucket_1 = MetricsBucket(metricsVersionId=1, date=self.today, hpoId="", metrics='{ "x": "a" }')
        metrics_bucket_2 = MetricsBucket(metricsVersionId=1, date=self.today, hpoId="PITT", metrics='{ "x": "b" }')

        metrics_bucket_3 = MetricsBucket(metricsVersionId=1, date=self.tomorrow, hpoId="", metrics='{ "y": "c" }')
        self.bucket_dao.insert(metrics_bucket_1)
        self.bucket_dao.insert(metrics_bucket_2)
        self.bucket_dao.insert(metrics_bucket_3)
        self.version_dao.set_pipeline_finished(True)

    def test_get_metrics_with_buckets_and_today_start_date_tomorrow_end_date(self):
        self.setup_buckets()
        response = self.send_post(
            "Metrics", {"start_date": self.today.isoformat(), "end_date": self.tomorrow.isoformat()}
        )
        self.assertEqual([self.expected_bucket_1, self.expected_bucket_2, self.expected_bucket_3], response)

    def test_get_metrics_with_buckets_and_today_start_end_date(self):
        self.setup_buckets()
        response = self.send_post(
            "Metrics", {"start_date": self.today.isoformat(), "end_date": self.today.isoformat()}
        )
        self.assertEqual([self.expected_bucket_1, self.expected_bucket_2], response)

    def test_get_metrics_with_buckets_and_tomorrow_start_end_date(self):
        self.setup_buckets()
        response = self.send_post(
            "Metrics", {"start_date": self.tomorrow.isoformat(), "end_date": self.tomorrow.isoformat()}
        )
        self.assertEqual([self.expected_bucket_3], response)

    def test_get_metrics_with_no_buckets_and_tomorrow_start_date_today_end_date(self):
        self.setup_buckets()
        response = self.send_post(
            "Metrics", {"start_date": self.tomorrow.isoformat(), "end_date": self.today.isoformat()}
        )
        self.assertEqual([], response)
