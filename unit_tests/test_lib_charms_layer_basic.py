import os
import mock

import lib.charms.layer.basic as basic

import unit_tests.utils as test_utils

from unittest.mock import patch


class TestLayerBasic(test_utils.BaseTestCase):

    def test__load_wheelhouse_versions(self):
        self.patch_object(basic, 'glob')
        self.patch_object(basic, 'LooseVersion')
        self.glob.return_value = [
            'python-dateutil-2.8.1.tar.gz',
            'setuptools_scm-1.17.0.tar.gz',
            'wheel-0.33.6.tar.gz',
        ]
        self.assertDictEqual(
            basic._load_wheelhouse_versions(), {
                'setuptools-scm': mock.ANY,
                'python-dateutil': mock.ANY,
                'wheel': mock.ANY,
            })
        self.LooseVersion.assert_has_calls([
            mock.call('0.33.6.tar.gz'),
            mock.call('2.8.1.tar.gz'),
            mock.call('1.17.0.tar.gz'),
        ], any_order=True)

    @patch.dict('os.environ', {'LANG': 'su_SU.UTF-8'})
    def test__get_subprocess_env_lang_set(self):
        env = basic._get_subprocess_env()
        self.assertEqual(env['LANG'], 'su_SU.UTF-8')
        self.assertEqual(dict(os.environ), env)

    def test__get_subprocess_env_lang_not_set(self):
        with mock.patch.dict('os.environ'):
            del os.environ['LANG']
            env = basic._get_subprocess_env()
            self.assertEqual(env['LANG'], 'C.UTF-8')
            # The only difference between dicts is the lack of LANG
            # in os.environ.
            self.assertEqual({key for key in set(env) - set(os.environ)},
                             {'LANG'})
