import os
import copy
import mock

from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)

HANDLER_PATH = 'pdcupdater.handlers.modules.ModuleStateChangeHandler'
ARCHES = ['aarch64', 'armv7hl', 'i686', 'ppc64', 'ppc64le', 's390x', 'x86_64']


def mocked_koji_from_tag(url, tag):
    rpm_id = 12584426
    rpms = []
    for arch in ARCHES:
        for package in ['ed-debuginfo', 'ed-debugsource', 'ed']:
            rpms.append({
                'arch': arch,
                'build_id': 1020113,
                'buildroot_id': 11153004,
                'buildtime': 1516728736,
                'epoch': None,
                'extra': None,
                'id': rpm_id,
                'metadata_only': False,
                'name': package,
                'release': '1.module_1503+67eff7c7',
                'srpm_name': 'ed',
                'srpm_nevra': 'ed-1.14.2-1.module_1503+67eff7c7',
                'version': '1.14.2'
            })
            rpm_id -= 1
    rpms.append({
        'arch': 'src',
        'build_id': 1020113,
        'buildroot_id': 11153004,
        'buildtime': 1516728733,
        'epoch': None,
        'extra': None,
        'id': rpm_id,
        'metadata_only': False,
        'name': 'ed',
        'release': '1.module_1503+67eff7c7',
        'srpm_name': 'ed',
        'srpm_nevra': 'ed-1.14.2-1.module_1503+67eff7c7',
        'version': '1.14.2'
    })
    return rpms


def get_expected_rpms():
    expected_rpms = []
    for arch in ARCHES:
        for package in ['ed-debuginfo', 'ed-debugsource', 'ed']:
            expected_rpms.append({
                'arch': arch,
                'epoch': 0,
                'name': package,
                'release': '1.module_1503+67eff7c7',
                'srpm_name': 'ed',
                'srpm_nevra': 'ed-1.14.2-1.module_1503+67eff7c7',
                'version': '1.14.2'
            })
    expected_rpms.append({
        'arch': 'src',
        'epoch': 0,
        'name': 'ed',
        'release': '1.module_1503+67eff7c7',
        'srpm_name': 'ed',
        'srpm_commit_branch': 'master',
        'srpm_commit_hash': '51f529a5cde2b843ed9c7870689d707eaab3a9d1',
        'version': '1.14.2'
    })
    return expected_rpms


class TestModuleStateChange(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.modules:ModuleStateChangeHandler'
    test_data_dir = os.path.join(
        os.path.dirname(__file__), "test_modules_data")
    with open(os.path.join(test_data_dir, "modulemd.yaml")) as f:
        modulemd_example = f.read()

    state_wait_msg = {
        'topic': 'org.fedoraproject.prod.mbs.module.state.change',
        'msg': {
            'tasks': {},
            'state_name': 'wait',
            'stream': 'master',
            'owner': 'mprahl',
            'id': 1503,
            'state_reason': None,
            'time_completed': None,
            'build_context': '3044bea5ac56e79502c45b08536a51d5a9e0a88e',
            'state': 1,
            'version': '20180123171544',
            'koji_tag': None,
            'scmurl': ('https://src.fedoraproject.org/modules/testmodule.git'
                       '?#1d28a6e2e4fd604d98be0322ef0c0c4a931f091d'),
            'state_trace': [],
            'rebuild_strategy': 'all',
            'runtime_context': '3044bea5ac56e79502c45b08536a51d5a9e0a88e',
            'state_url': None,
            'component_builds': [
                91387
            ],
            'name': 'testmodule',
            'time_submitted': '2018-01-23T17:15:57Z',
            'time_modified': '2018-01-23T17:16:02Z',
            'modulemd': modulemd_example,
            'context': 'c2c572ec'
        }
    }
    state_ready_msg = copy.deepcopy(state_wait_msg)
    state_ready_msg['msg'].update({
        'tasks': {
            'rpms': {
                'ed': {
                    'state': 1,
                    'nvr': 'ed-1.14.2-1.module_1503+67eff7c7',
                    'task_id': 24401846,
                    'state_reason': ''
                },
                'module-build-macros': {
                    'state': 1,
                    'nvr': ('module-build-macros-0.1-1.module_1503'
                            '+67eff7c7'),
                    'task_id': 24401602,
                    'state_reason': ''
                }
            }
        },
        'state_name': 'ready',
        'id': 1503,
        'time_completed': '2018-01-23T17:34:06Z',
        'state': 5,
        'koji_tag': 'module-ce2adf69caf0e1b5',
        'component_builds': [
            91387,
            91388
        ],
        'time_modified': '2018-01-23T17:34:11Z'
    })
    # On the new "modules" PDC API, the context is used to generate the Koji
    # tag
    state_ready_new_api_msg = copy.deepcopy(state_ready_msg)
    state_ready_new_api_msg['msg'].update({'koji_tag': '67eff7c74088acdf'})

    @mock.patch(HANDLER_PATH + '.get_pdc_api')
    @mock_pdc
    def test_create_unreleased_variant_exists(self, pdc, get_api):
        # Test the old API
        get_api.return_value = 'unreleasedvariants'
        self.handler.handle(pdc, self.state_wait_msg)
        self.assertEqual(len(pdc.calls['unreleasedvariants']), 1)
        self.assertEqual(pdc.calls['unreleasedvariants'][0][0], 'GET')
        expected_get = {
            'variant_uid': 'testmodule:master:20180123171544',
            'page_size': -1
        }
        self.assertDictEqual(
            pdc.calls['unreleasedvariants'][0][1], expected_get)

    @mock.patch(HANDLER_PATH + '.get_pdc_api')
    @mock_pdc
    def test_create_unreleased_variant(self, pdc, get_api):
        # Test the old API
        get_api.return_value = 'unreleasedvariants'
        # Remove the data returned from the API since the test PDC client
        # doesn't seem to understand filtering and pdc-updater will think it
        # doesn't need to create the entry
        pdc.endpoints['unreleasedvariants']['GET'] = []
        self.handler.handle(pdc, self.state_wait_msg)
        self.assertEqual(len(pdc.calls['unreleasedvariants']), 2)
        self.assertEqual(pdc.calls['unreleasedvariants'][0][0], 'GET')
        expected_get = {
            'variant_uid': 'testmodule:master:20180123171544',
            'page_size': -1
        }
        self.assertDictEqual(
            pdc.calls['unreleasedvariants'][0][1], expected_get)
        self.assertEqual(pdc.calls['unreleasedvariants'][1][0], 'POST')
        expected_post = {
            'build_deps': [{'dependency': 'platform', 'stream': 'f28'}],
            'koji_tag': 'module-ce2adf69caf0e1b5',
            'modulemd': self.modulemd_example,
            'runtime_deps': [{'dependency': 'platform', 'stream': 'f28'}],
            'variant_id': 'testmodule',
            'variant_name': 'testmodule',
            'variant_release': '20180123171544',
            'variant_type': 'module',
            'variant_uid': 'testmodule:master:20180123171544',
            'variant_version': 'master'
        }
        self.assertDictEqual(
            pdc.calls['unreleasedvariants'][1][1], expected_post)

    @mock.patch(HANDLER_PATH + '.get_pdc_api')
    @mock.patch(HANDLER_PATH + '.get_module_rpms')
    @mock_pdc
    def test_update_unreleased_variant(self, pdc, get_rpms, get_api):
        # Test the old API
        get_api.return_value = 'unreleasedvariants'
        get_rpms.return_value = get_expected_rpms()
        self.handler.handle(pdc, self.state_ready_msg)
        # Make sure a GET request was made to get the module
        self.assertEqual(pdc.calls['unreleasedvariants'][0][0], 'GET')
        # Make sure the PATCH was sent on the module
        endpoint = 'unreleasedvariants/testmodule:master:20180123171544'
        self.assertEqual(pdc.calls[endpoint][0][0], 'PATCH')
        self.assertEqual(
            set(pdc.calls[endpoint][0][1].keys()), set(['active', 'rpms']))

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_get_module_rpms(self, pdc, koji):
        koji.side_effect = mocked_koji_from_tag

        variant = {}
        variant["koji_tag"] = "epel7"
        variant["modulemd"] = self.modulemd_example

        expected_rpms = get_expected_rpms()
        rpms = self.handler.get_module_rpms(pdc, variant)
        self.assertEqual(expected_rpms, rpms)

    @mock_pdc
    def test_create_module(self, pdc):
        # Remove the data returned from the API since the test PDC client
        # doesn't seem to understand filtering and pdc-updater will think it
        # doesn't need to create the entry
        pdc.endpoints['modules']['GET'] = []
        self.handler.handle(pdc, self.state_wait_msg)
        self.assertEqual(len(pdc.calls['modules']), 3)
        # The API version check here
        self.assertEqual(pdc.calls['modules'][0][0], 'GET')
        self.assertDictEqual(pdc.calls['modules'][0][1], {'page_size': 1})
        # The GET check using the context
        self.assertEqual(pdc.calls['modules'][1][0], 'GET')
        expected_get = {
            'uid': 'testmodule:master:20180123171544:c2c572ec',
            'page_size': -1
        }
        self.assertDictEqual(pdc.calls['modules'][1][1], expected_get)
        self.assertEqual(pdc.calls['modules'][2][0], 'POST')
        expected_post = {
            'build_deps': [{'dependency': 'platform', 'stream': 'f28'}],
            'koji_tag': 'module-67eff7c74088acdf',
            'modulemd': self.modulemd_example,
            'runtime_deps': [{'dependency': 'platform', 'stream': 'f28'}],
            'name': 'testmodule',
            'version': '20180123171544',
            'stream': 'master',
            'context': 'c2c572ec',
        }
        self.assertDictEqual(pdc.calls['modules'][2][1], expected_post)

    @mock_pdc
    def test_create_module_exists(self, pdc):
        self.handler.handle(pdc, self.state_wait_msg)
        # The API version check here
        self.assertEqual(pdc.calls['modules'][0][0], 'GET')
        self.assertDictEqual(pdc.calls['modules'][0][1], {'page_size': 1})
        # The GET check using the context
        self.assertEqual(len(pdc.calls['modules']), 2)
        self.assertEqual(pdc.calls['modules'][1][0], 'GET')
        expected_get = {
            'uid': 'testmodule:master:20180123171544:c2c572ec',
            'page_size': -1
        }
        self.assertDictEqual(pdc.calls['modules'][1][1], expected_get)

    @mock.patch(HANDLER_PATH + '.get_module_rpms')
    @mock_pdc
    def test_update_module(self, pdc, get_rpms):
        get_rpms.return_value = get_expected_rpms()
        self.handler.handle(pdc, self.state_ready_new_api_msg)
        # The API version check here
        self.assertEqual(pdc.calls['modules'][0][0], 'GET')
        self.assertDictEqual(pdc.calls['modules'][0][1], {'page_size': 1})
        # Make sure a GET request was made to get the module
        self.assertEqual(pdc.calls['modules'][1][0], 'GET')
        # Make sure the PATCH was sent on the module
        endpoint = 'modules/testmodule:master:20180123171544:c2c572ec'
        self.assertEqual(pdc.calls[endpoint][0][0], 'PATCH')
        self.assertEqual(
            set(pdc.calls[endpoint][0][1].keys()), set(['active', 'rpms']))
