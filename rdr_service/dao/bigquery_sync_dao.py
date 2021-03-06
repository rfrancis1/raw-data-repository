from rdr_service.dao.base_dao import UpsertableDao
from rdr_service.model.bigquery_sync import BigQuerySync
from rdr_service.model.code import Code
from rdr_service.model.site import Site


class BigQuerySyncDao(UpsertableDao):

    def __init__(self, backup=False):
        """
        :param backup: Use backup readonly database connection.
        """
        super(BigQuerySyncDao, self).__init__(BigQuerySync, backup=backup)


class BigQueryGenerator(object):
    """
    Base class for generating BigQuery data JSON for storing in the bigquery_sync mysql table.
    """

    def save_bqrecord(self, pk_id, bqrecord, bqtable, w_dao, w_session, project_id=None):
        """
        Save the BQRecord object into the bigquery_sync table.
        :param pk_id: primary key id value from source table.
        :param bqrecord: BQRecord object.
        :param bqtable: BQTable object.
        :param w_dao: Writeable BigQuerySyncDao object
        :param w_session: Session from a writable BigQuerySyncDao object
        :param project_id: Project ID override value.
        """
        if not isinstance(pk_id, int):
            raise ValueError('Invalid primary key value, value must be an integer.')

        if not w_dao or not w_session:
            raise ValueError('Invalid BigQuerySyncDao dao or session argument.')

        # see if there is a project id override value.
        if project_id:
            cur_id = project_id
        else:
            cur_id = 'localhost'
            try:
                from rdr_service import config
                cur_id = config.GAE_PROJECT
                if not cur_id or cur_id == 'None':
                    cur_id = 'localhost'
            except ImportError:
                pass
            except AttributeError:
                pass

        mappings = bqtable.get_project_map(cur_id)

        for project_id, dataset_id, table_id in mappings:
            # If project_id is None, we shouldn't save records for this project.
            if dataset_id is None:
                # logging.warning('{0} is mapped to none in {1} project.'.format(project_id, cur_id))
                continue
            bqs_rec = w_session.query(BigQuerySync.id). \
                filter(BigQuerySync.pk_id == pk_id, BigQuerySync.projectId == project_id,
                       BigQuerySync.datasetId == dataset_id, BigQuerySync.tableId == table_id).first()

            bqs = BigQuerySync()
            bqs.id = bqs_rec.id if bqs_rec else None
            bqs.pk_id = pk_id
            bqs.projectId = project_id
            bqs.datasetId = dataset_id
            bqs.tableId = table_id
            bqs.resource = bqrecord.to_dict(serialize=True)
            w_dao.upsert_with_session(w_session, bqs)
            # we don't call session flush here, because we might be part of a batch process.

    def _merge_schema_dicts(self, dict1, dict2):
        """
        Safely merge dict2 schema into dict1 schema
        :param dict1: dict object
        :param dict2: dict object
        :return: dict
        """
        lists = {key: val for key, val in dict1.items()}
        dict1.update(dict2)
        for key, val in lists.items():  # pylint: disable=unused-variable
            if key in dict2:
                # This assumes all sub-tables are set to repeated (multi-row) type.
                dict1[key] = lists[key] + dict2[key]

        return dict1

    def _lookup_code_value(self, code_id, session):
        """
        Return the code id string value from the code table.
        :param code_id: codeId from code table
        :param session: DAO session object
        :return: string
        """
        if code_id is None:
            return None
        result = session.query(Code.value).filter(Code.codeId == int(code_id)).first()
        if not result:
            return None
        return result.value

    def _lookup_code_id(self, code, ro_session):
        """
        Return the code id for the given code value string.
        :param code: code value string
        :param ro_session: ReadOnly DAO session object
        :return: int
        """
        if code is None:
            return None
        result = ro_session.query(Code.codeId).filter(Code.value == code).first()
        if not result:
            return None
        return result.codeId

    def _lookup_site_name(self, site_id, ro_session):
        """
        Look up the site name
        :param site_id: site id integer
        :param ro_session: Readonly DAO session object
        :return: string
        """
        site = ro_session.query(Site.googleGroup).filter(Site.siteId == site_id).first()
        if not site:
            return None
        return site.googleGroup
