from flask import request
from flask_restful import Resource
from werkzeug import exceptions

from rdr_service import app_util
from rdr_service.api_util import STOREFRONT
from rdr_service.dao.metric_set_dao import AggregateMetricsDao, MetricSetDao
from rdr_service.participant_enums import METRIC_SET_KEYS, MetricsKey


class MetricSetsApi(Resource):
    @app_util.auth_required(STOREFRONT)
    def get(self, ms_id=None):
        if ms_id:
            return self._get_aggregates(ms_id)

        msets = MetricSetDao().get_all()
        return {"metricSets": [MetricSetDao.to_client_json(ms) for ms in msets]}

    def _get_aggregates(self, ms_id):
        keyset = set()
        for key in request.args.getlist("keys"):
            if key not in MetricsKey.to_dict():
                raise exceptions.BadRequest("unknown metrics key {}".format(key))
            keyset.add(MetricsKey.lookup_by_name(key))

        ms = MetricSetDao().get(ms_id)
        if not ms:
            raise exceptions.NotFound('metric set "{}" not found'.format(ms_id))

        if not keyset.issubset(METRIC_SET_KEYS[ms.metricSetType]):
            raise exceptions.BadRequest(
                "unexpected metric keys for metric set of type {}: {}".format(
                    ms.metricSetType.name, [k.name for k in keyset - METRIC_SET_KEYS[ms.metricSetType]]
                )
            )

        aggs = AggregateMetricsDao().get_all_for_metric_set(ms_id)
        if keyset:
            aggs = [agg for agg in aggs if agg.metricsKey in keyset]
        return {"metrics": AggregateMetricsDao.to_client_json(aggs)}
