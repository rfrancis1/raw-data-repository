"""The API definition for the config API."""
import json
import logging
import os

from flask import request
from flask_restful import Resource
from google.cloud import datastore as ndb  # pylint: disable=unused-import
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from rdr_service import app_util, config
from rdr_service.config import GAE_PROJECT
from rdr_service.api_util import parse_date
from rdr_service.app_util import get_oauth_id


# Read bootstrap config admin service account configuration
CONFIG_ADMIN_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", "config_admins.json")

with open(CONFIG_ADMIN_FILE) as config_file:
    try:
        CONFIG_ADMIN_MAP = json.load(config_file)
    except IOError:
        logging.error(f"Unable to load config admin file {CONFIG_ADMIN_FILE}.")
        CONFIG_ADMIN_MAP = {}


def auth_required_config_admin(func):
    """A decorator that checks that the caller is a config admin for the app."""

    def wrapped(*args, **kwargs):
        check_config_admin()
        return func(*args, **kwargs)

    return wrapped


def is_config_admin(user_email):
    # Allow clients to simulate an unauthentiated request (for testing)
    # becaues we haven't found another way to create an unauthenticated request
    # when using dev_appserver. When client tests are checking to ensure that an
    # unauthenticated requests gets rejected, they helpfully add this header.
    # The `application_id` check ensures this feature only works in dev_appserver.
    if GAE_PROJECT == "localhost" and request.headers.get("unauthenticated"):
        user_email = None

    if user_email:
        config_admin = CONFIG_ADMIN_MAP.get(GAE_PROJECT, "configurator@{}.iam.gserviceaccount.com".format(GAE_PROJECT))
        if user_email == config_admin or user_email == 'example@example.com':
            return True
    return False


def check_config_admin():
    """Raises Unauthorized unless the caller is a config admin."""
    user_email = app_util.get_oauth_id()
    if is_config_admin(user_email):
        logging.info(f"User {user_email} ALLOWED for config endpoint")
        return
    logging.info(f"User {user_email} NOT ALLOWED for config endpoint")
    raise Forbidden()


class ConfigApi(Resource):
    """Api handlers for retrieving and setting config values."""

    method_decorators = [auth_required_config_admin]

    def get(self, key=config.CONFIG_SINGLETON_KEY):
        date = request.args.get("date")
        if date is not None:
            date = parse_date(date)
        config_obj = config.load(key, date=date)
        if config_obj:
            return config_obj
        elif key == config.CONFIG_SINGLETON_KEY:
            return {}
        else:
            raise NotFound(f'config not found: {key}')

    def post(self, key=config.CONFIG_SINGLETON_KEY):
        config_obj = request.get_json(force=True)
        self.validate(key, config_obj)
        config.store(key, config_obj)
        return config_obj

    def put(self, key=config.CONFIG_SINGLETON_KEY):
        old_config = config.load(key)
        if old_config is None:
            raise NotFound(f'config not found: {key}')

        config_obj = request.get_json(force=True)

        date = None
        if config.getSettingJson(config.ALLOW_NONPROD_REQUESTS, False):
            date = request.headers.get("x-pretend-date", None)
        if date is not None:
            date = parse_date(date)

        client_id = get_oauth_id()

        config.store(key, config_obj, date=date, client_id=client_id)
        return config_obj

    def validate(self, name, config_obj):
        if name == config.CONFIG_SINGLETON_KEY:
            # make sure all required keys are present and that the values are the right type.
            for k in config.REQUIRED_CONFIG_KEYS:
                if k not in config_obj:
                    raise BadRequest("Missing required config key {}".format(k))
                val = config_obj[k]
                if not isinstance(val, list) or [v for v in val if not isinstance(v, str)]:
                    raise BadRequest("Config for {} must be a list of strings".format(k))
