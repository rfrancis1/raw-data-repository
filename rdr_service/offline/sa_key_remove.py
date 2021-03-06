import logging
from datetime import datetime

from rdr_service.config import GAE_PROJECT
from googleapiclient import discovery

from rdr_service import config

"""Deletes service account keys older than 3 days as required by NIH"""


def delete_service_account_keys():
    days_to_delete = config.getSetting(config.DAYS_TO_DELETE_KEYS)
    service_accounts_with_long_lived_keys = config.getSettingList(
        config.SERVICE_ACCOUNTS_WITH_LONG_LIVED_KEYS, default=[]
    )
    app_id = GAE_PROJECT
    if app_id is None:
        return

    project_name = "projects/" + app_id
    try:
        service = discovery.build("iam", "v1", cache_discovery=False)
        request = service.projects().serviceAccounts().list(name=project_name)
        response = request.execute()
        accounts = response["accounts"]

        for account in accounts:
            if account["email"] in service_accounts_with_long_lived_keys:
                logging.info("Skip key expiration check for Service Account {}".format(account))
                continue

            serviceaccount = project_name + "/serviceAccounts/" + account["email"]
            request = service.projects().serviceAccounts().keys().list(
                name=serviceaccount, keyTypes="USER_MANAGED"
            )
            response = request.execute()
            if "keys" in response:
                keys = response["keys"]

                for key in keys:
                    keyname = key["name"]
                    startdate = datetime.strptime(key["validAfterTime"], "%Y-%m-%dT%H:%M:%SZ")

                    key_age_days = (datetime.utcnow() - startdate).days

                    if key_age_days >= days_to_delete:
                        logging.warning(
                            "Deleting service Account key older than {} days [{}]: {}".format(
                                days_to_delete, key_age_days, keyname
                            )
                        )

                        delete_request = service.projects().serviceAccounts().keys().delete(name=keyname)
                        delete_request.execute()
                    else:
                        logging.info("Service Account key is {} days old: {}".format(key_age_days, keyname))

    except KeyError:
        logging.info('No Service Accounts found in project "{}"'.format(app_id))
