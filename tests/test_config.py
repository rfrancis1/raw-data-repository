import datetime
import http.client
import os
import os.path
import shutil
import tempfile
import unittest

from mock import patch

from rdr_service import config
from rdr_service.clock import FakeClock
from tests.helpers.unittest_base import BaseTestCase

class TestConfig(BaseTestCase):

    def setUp(self):
        super().setUp()
        _test_config_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, _test_config_dir)
        _old_config_root = os.environ.get('RDR_CONFIG_ROOT', None)

        current_config_path = os.path.abspath(os.path.join(config.LocalFilesystemConfigProvider.get_config_root(),
                                                           'current_config.json'))
        shutil.copyfile(
            current_config_path,
            os.path.abspath(os.path.join(_test_config_dir, 'current_config.json'))
        )

        os.environ['RDR_CONFIG_ROOT'] = _test_config_dir
        self.addCleanup(os.environ.__setitem__, 'RDR_CONFIG_ROOT', _old_config_root)

    def test_GET_main_config(self):
        from_api = self.send_get("Config")
        from_py = config.get_config()
        self.assertEqual(from_api, from_py)

    def test_GET_nonexistent_config_is_404(self):
        bad_path = "Config/nonsense"
        self.send_get(bad_path, expected_status=http.client.NOT_FOUND)

    @unittest.skip("only run manually, doesn't support date.")
    def test_GET_config_by_date(self):
        t1 = datetime.datetime(2018, 1, 1)
        t2 = t1 + datetime.timedelta(days=1)
        # Use a custom config so the output is easier to parse on failure
        name = "xxx"
        path = "Config/{}".format(name)
        conf = {"test_key": ["original", "values"]}

        # Create the configuration; verify it is created
        with FakeClock(t1):
            response = self.send_post(path, request_data=conf)
            self.assertEqual(conf, response)
            self.assertEqual(conf, config.load(name))

        with FakeClock(t2):
            # Alter the configuration; verify it is altered
            conf_A = {"test_key": ["new", "values"]}
            self.send_put(path, request_data=conf_A)
            response_A = self.send_get(path)
            self.assertEqual(conf_A, response_A)
            self.assertEqual(conf_A, config.load(name))

            # Fetch the first configuration; verify it is preserved
            response_B = self.send_get("{}?date={}".format(path, t1.isoformat()))
            self.assertEqual(response_B, conf)
            self.assertEqual(response_B, config.load(name, date=t1))

    def test_PUT_main_config(self):
        existing = config.get_config()
        existing["test"] = ["some", "values"]
        self.send_put("Config", request_data=existing)
        altered = self.send_get("Config")
        self.assertEqual(altered, existing)

    def test_PUT_nonexistent_config_is_404(self):
        bad_path = "Config/nonsense"
        data = {"some": ["stuff"]}
        self.send_put(bad_path, request_data=data, expected_status=http.client.NOT_FOUND)

    def test_POST_random_config(self):
        other_config = {"foo": "bar"}
        self.send_post("Config/xxx", other_config)
        response = self.send_get("Config/xxx")
        self.assertEqual(other_config, response)

    @patch("rdr_service.config.REQUIRED_CONFIG_KEYS", new=["i_am_required"])
    def test_POST_main_config_without_required_keys_is_400(self):
        bad_config = {"not_required": ["some other value"]}
        self.send_post("Config", request_data=bad_config, expected_status=http.client.BAD_REQUEST)

    def test_POST_main_config_with_malformed_config_is_400(self):
        # The config is a mapping to lists of strings - no other value is acceptable
        # This is not an exhaustive check, just a sanity check that we do in fact get 400 for non
        # list[string] values.
        bad_config = {"some key": "not a list"}
        self.send_post("Config", request_data=bad_config, expected_status=http.client.BAD_REQUEST)

    @patch("rdr_service.config.REQUIRED_CONFIG_KEYS", new=["i_am_required"])
    def test_POST_does_not_validate_random_config(self):
        rando_config = {"not_required": "not a list"}
        self.send_post("Config/rando_config", request_data=rando_config)
