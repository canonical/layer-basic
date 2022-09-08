import os
import mock
import subprocess

import lib.charms.layer.basic as basic

import unit_tests.utils as test_utils

from unittest.mock import patch


class TestLayerBasic(test_utils.BaseTestCase):

    wheelhouse_glob = [
        'python-dateutil-2.8.1.tar.gz',
        'setuptools_scm-1.17.0.tar.gz',
        'wheel-0.33.6.tar.gz',
        'cffi-1.15.1'
        '-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl',
        'flit_core-3.7.1-py3-none-any.whl',
    ]

    def test__load_wheelhouse_versions(self):
        self.patch_object(basic, 'glob')
        self.patch_object(basic, 'LooseVersion')
        self.glob.return_value = self.wheelhouse_glob
        self.assertDictEqual(
            basic._load_wheelhouse_versions(), {
                'setuptools-scm': mock.ANY,
                'python-dateutil': mock.ANY,
                'wheel': mock.ANY,
                'cffi': mock.ANY,
                'flit-core': mock.ANY,
            })
        self.LooseVersion.assert_has_calls([
            mock.call('0.33.6.tar.gz'),
            mock.call('2.8.1.tar.gz'),
            mock.call('1.17.0.tar.gz'),
            mock.call('1.15.1'),
            mock.call('3.7.1'),
        ], any_order=True)
        self.assertEqual(
            self.LooseVersion.call_count,
            5)

    def test__add_back_versions(self):
        self.patch_object(basic, 'glob')
        self.glob.return_value = self.wheelhouse_glob
        self.assertEqual(
            basic._add_back_versions(
                [
                    'python-dateutil',
                    'setuptools-scm',
                    'wheel',
                    'cffi',
                    'flit-core',
                ],
                basic._load_wheelhouse_versions()),
            [
                'python-dateutil==2.8.1',
                'setuptools-scm==1.17.0',
                'wheel==0.33.6',
                'cffi==1.15.1',
                'flit-core==3.7.1'
            ])

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

    def test__load_installed_versions(self):
        self.patch_object(basic, 'LooseVersion')
        with mock.patch('lib.charms.layer.basic.check_output') as reqs:
            reqs.return_value = b"""
# comments are ignored
wget==3.2
zope.interface==4.3.2
ignored>=1.2.3
-e git+git+ssh://git.launchpad.net/git-project"""
            installed = basic._load_installed_versions("path/to/pip")
        self.assertDictEqual(installed, {
            "wget": mock.ANY,
            "zope.interface": mock.ANY,
        })
        self.LooseVersion.assert_has_calls([
            mock.call('3.2'),
            mock.call('4.3.2'),
        ], any_order=False)

    @mock.patch('lib.charms.layer.basic.check_call')
    @mock.patch('lib.charms.layer.basic.sleep')
    def test__apt_install(self, sleep, check_call):
        def fake_check_call(*args, **kwargs):
            raise subprocess.CalledProcessError(basic.APT_NO_LOCK, ['apt-get'])

        check_call.side_effect = fake_check_call
        self.assertRaises(subprocess.CalledProcessError,
                          basic.apt_install, ["coreutils"])
        self.assertEqual(len(check_call.mock_calls),
                         # `apt-get install` and `apt-get update` are run, but
                         # in the last iteration `apt-get update` is not
                         # executed.
                         basic.CMD_RETRY_COUNT * 2 - 1)
        sleep.assert_called_with(basic.CMD_RETRY_DELAY)
        self.assertEqual(len(sleep.mock_calls), basic.CMD_RETRY_COUNT - 1)
