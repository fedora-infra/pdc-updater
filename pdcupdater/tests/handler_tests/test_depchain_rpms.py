import mock

import pdcupdater.utils
from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)


class TestBuildtimeDepIngestion(BaseHandlerTest):
    maxDiff = None
    handler_path = 'pdcupdater.handlers.depchain.rpms:NewRPMBuildTimeDepChainHandler'
    config = {}

    def test_can_handle_buildsys_tag_message(self):
        idx = '2016-5af8c0c2-9acd-4cf4-afa6-c07649bb5561'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, True)

    @mock_pdc
    def test_handle_new_build(self, pdc):
        idx = '2016-5af8c0c2-9acd-4cf4-afa6-c07649bb5561'
        msg = pdcupdater.utils.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        expected_keys = [
            'release-component-relationships',
            'releases/fedora-26',
            'release-components',
            'global-components',
        ]
        self.assertEquals(pdc.calls.keys(), expected_keys)

        self.assertEqual(len(pdc.calls['global-components']), 53116)
        self.assertEqual(len(pdc.calls['release-components']), 53116)
        self.assertEqual(len(pdc.calls['release-component-relationships']), 17705)

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_list_buildroot_for')
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    @mock.patch('pdcupdater.services.koji_builds_in_tag')
    def test_audit_empty_koji(self, pdc, builds, rpms, buildroot):

        # Mock out koji results
        builds.return_value = [{
            'build_id': 'fake_build_id',
            'name': 'guake',
        }]
        rpms.return_value = {}, []
        buildroot.return_value = 'wat2'

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-component-relationships': [
                ('GET', {'page': 1, 'release': 'fedora-26', 'type': 'RPMBuildRequires'}),
                ('GET', {'page': 1, 'release': 'fedora-26', 'type': 'RPMBuildRoot'}),
            ],
            'releases/fedora-26': [('GET', {})]
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_list_buildroot_for')
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    @mock.patch('pdcupdater.services.koji_builds_in_tag')
    def test_audit_mismatch(self, pdc, builds, rpms, buildroot):

        # Mock out koji results
        _build = {
            'build_id': 'fake_build_id',
            'name': 'guake',
        }
        builds.return_value = [_build]
        rpms.return_value = _build, ['some rpm filename']
        buildroot.return_value = [
            { 'name': 'buildtimelib1', 'is_update': True, },
            { 'name': 'buildtimelib2', 'is_update': False, },
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-component-relationships': [
                ('GET', {'page': 1, 'release': 'fedora-26', 'type': 'RPMBuildRequires'}),
                ('GET', {'page': 1, 'release': 'fedora-26', 'type': 'RPMBuildRoot'}),
            ],
            'releases/fedora-26': [('GET', {})]
        })

        # Check the results.
        self.assertSetEqual(present, set([]))
        self.assertSetEqual(absent, set([
            'guake/fedora-26 RPMBuildRequires buildtimelib1/fedora-26',
            'guake/fedora-26 RPMBuildRoot buildtimelib2/fedora-26',
        ]))


class TestRuntimeDepIngestion(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.depchain.rpms:NewRPMRunTimeDepChainHandler'
    config = {}

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_yield_rpm_requires')
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    @mock.patch('pdcupdater.services.koji_builds_in_tag')
    def test_audit_mismatch(self, pdc, builds, rpms, requires):

        # Mock out koji results
        _build = {
            'build_id': 'fake_build_id',
            'name': 'guake',
        }
        builds.return_value = [_build]
        rpms.return_value = _build, ['some rpm filename']
        requires.return_value = [
            ('runtimelib1', '', '',),
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-component-relationships': [ ('GET', {
                'page': 1, 'release': 'fedora-26', 'type': 'RPMRequires'
            })],
            'releases/fedora-26': [('GET', {})]
        })

        # Check the results.
        self.assertSetEqual(present, set(['guake/fedora-26 RPMRequires nethack/fedora-26']))
        self.assertSetEqual(absent, set(['guake/fedora-26 RPMRequires runtimelib1/fedora-26']))

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_yield_rpm_requires')
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    @mock.patch('pdcupdater.services.koji_builds_in_tag')
    def test_audit_simple_match(self, pdc, builds, rpms, requires):
        # Mock out koji results
        _build = {
            'build_id': 'fake_build_id',
            'name': 'guake',
        }
        builds.return_value = [_build]
        rpms.return_value = _build, ['some rpm filename']
        requires.return_value = [
            ('nethack', '', '',),
        ]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-component-relationships': [ ('GET', {
                'page': 1, 'release': 'fedora-26', 'type': 'RPMRequires'
            })],
            'releases/fedora-26': [('GET', {})]
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_yield_rpm_requires')
    @mock.patch('pdcupdater.services.koji_rpms_from_build')
    @mock.patch('pdcupdater.services.koji_builds_in_tag')
    def test_initialize(self, pdc, builds, rpms, requires):
        # Mock out koji results
        _build = {
            'build_id': 'fake_build_id',
            'name': 'guake',
        }
        builds.return_value = [_build]
        rpms.return_value = _build, ['some rpm filename']
        requires.return_value = [
            ('nethack', '', '',),
        ]

        # Call the initializer
        self.handler.initialize(pdc)

        # Check the PDC calls..

        expected_calls = {
            'global-components': [
                ('GET', {'name': 'guake'}),
                ('GET', {'name': 'nethack'}),
                ('GET', {'name': 'guake'}),
                ('GET', {'name': 'nethack'})
            ],
            'release-component-relationships': [
                ('POST',
                 {'child': {'name': 'nethack',
                            'release': {'release_id': 'fedora-26'}},
                  'parent': {'name': 'guake',
                             'release': {'release_id': 'fedora-26'}},
                  'type': 'RPMRequires'})],
            'release-components': [
                ('POST',
                 {'global_component': 'guake',
                  'name': 'guake',
                  'release': 'fedora-26',
                  'type': 'rpm'}),
                ('POST',
                 {'global_component': 'nethack',
                  'name': 'nethack',
                  'release': 'fedora-26',
                  'type': 'rpm'}),
                ('POST',
                 {'global_component': 'guake',
                  'name': 'guake',
                  'release': 'fedora-26',
                  'type': 'rpm'}),
                ('POST',
                 {'global_component': 'nethack',
                  'name': 'nethack',
                  'release': 'fedora-26',
                  'type': 'rpm'})],
            'releases/fedora-26': [('GET', {}), ('GET', {})]
        }

        self.assertDictEqual(pdc.calls, expected_calls)
