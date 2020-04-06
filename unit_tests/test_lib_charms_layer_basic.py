import mock

import lib.charms.layer.basic as basic

import unit_tests.utils as test_utils


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
