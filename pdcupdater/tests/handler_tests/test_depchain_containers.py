import mock

import pdcupdater.utils
from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)


class TestInclusionDepIngestion(BaseHandlerTest):
    maxDiff = None
    handler_path = 'pdcupdater.handlers.depchain.containers:ContainerRPMInclusionDepChainHandler'
    config = {}

    @mock.patch('pdcupdater.utils.rawhide_tag')
    @mock.patch('pdcupdater.utils.interesting_container_tags')
    def test_can_handle_buildsys_tag_message(self, tags, rawhide):
        tags.return_value = ['f24-docker']
        rawhide.return_value = 'f24'
        idx = '2016-b78e670b-e8f7-4987-868e-1260cc0f3fbd'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, True)

    @mock_pdc
    @mock.patch('pdcupdater.utils.rawhide_tag')
    @mock.patch('pdcupdater.utils.interesting_container_tags')
    @mock.patch('pdcupdater.services.koji_rpms_from_archive')
    @mock.patch('pdcupdater.services.koji_archives_from_build')
    @mock.patch('pdcupdater.services.koji_get_build')
    def test_handle_new_build(self, pdc, get_build, archives, rpms, tags, rawhide):
        tags.return_value = ['f24']
        rawhide.return_value = 'f24'
        container_build = {
            'build_id': 'fake_build_id',
            'name': 'cockpit', 'version': 1, 'release': 2, 'arch': 'foo',
        }
        rpm_build = {
            'build_id': 'fake_build_id',
            'name': 'guake', 'version': 1, 'release': 2, 'arch': 'foo',
        }
        get_build.return_value = container_build
        archives.return_value = [{
            'build_id': 802427,
            'buildroot_id': 6459519,
            'checksum': 'bf81b182dfbbf331ddd5700327abb4fe',
            'checksum_type': 0,
            'extra': 'stuff goes here...',
            'filename': 'docker-image-e3be590239f.x86_64.tar.gz',
            'id': 14707,
            'metadata_only': False,
            'size': 199457398,
            'type_description': 'Tar files',
            'type_extensions': 'tar tar.gz tar.bz2 tar.xz',
            'type_id': 4,
            'type_name': 'tar',
        }]
        rpms.return_value = [rpm_build]

        idx = '2016-b78e670b-e8f7-4987-868e-1260cc0f3fbd'
        msg = pdcupdater.utils.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        expected_keys = [
            'release-component-relationships',
            'releases/fedora-24-updates',
            'release-components',
            'global-components',
        ]
        self.assertEquals(pdc.calls.keys(), expected_keys)

        self.assertEqual(len(pdc.calls['global-components']), 1)
        self.assertEqual(len(pdc.calls['release-components']), 1)
        self.assertEqual(len(pdc.calls['release-component-relationships']), 2)

    @mock_pdc
    @mock.patch('pdcupdater.utils.rawhide_tag')
    @mock.patch('pdcupdater.utils.interesting_tags')
    @mock.patch('pdcupdater.services.koji_rpms_from_archive')
    @mock.patch('pdcupdater.services.koji_archives_from_build')
    @mock.patch('pdcupdater.services.koji_builds_in_tag')
    @mock.patch('pdcupdater.services.koji_get_build')
    def test_audit_empty_koji(self, pdc, get_build, builds, archives, rpms, tags, rawhide):
        tags.return_value = ['f24']
        rawhide.return_value = 'f24'

        # Mock out koji results
        build = {
            'build_id': 'fake_build_id',
            'name': 'guake',
            'version': 1,
            'release': 2,
            'arch': 'foo',
        }
        get_build.return_value = build
        builds.return_value = [build]
        archives.return_value = [{
            'build_id': 802427,
            'buildroot_id': 6459519,
            'checksum': 'bf81b182dfbbf331ddd5700327abb4fe',
            'checksum_type': 0,
            'extra': 'stuff goes here...',
            'filename': 'docker-image-e3be590239f.x86_64.tar.gz',
            'id': 14707,
            'metadata_only': False,
            'size': 199457398,
            'type_description': 'Tar files',
            'type_extensions': 'tar tar.gz tar.bz2 tar.xz',
            'type_id': 4,
            'type_name': 'tar'}
        ]
        rpms.return_value = []

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-component-relationships': [
                ('GET', {
                    'page': 1,
                    'from_component_release': 'fedora-24-updates',
                    'type': 'ContainerIncludesRPM',
                }),
                ('GET', {
                    'page': 1,
                    'from_component_release': 'fedora-24-updates',
                    'type': 'ContainerIncludesRPM',
                }),
            ],
            'releases/fedora-24-updates': [('GET', {}), ('GET', {})]
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set())


    @mock_pdc
    @mock.patch('pdcupdater.utils.rawhide_tag')
    @mock.patch('pdcupdater.utils.interesting_tags')
    @mock.patch('pdcupdater.services.koji_rpms_from_archive')
    @mock.patch('pdcupdater.services.koji_archives_from_build')
    @mock.patch('pdcupdater.services.koji_builds_in_tag')
    @mock.patch('pdcupdater.services.koji_get_build')
    def test_audit_mismatch(self, pdc, get_build, builds, archives, rpms, tags, rawhide):
        tags.return_value = ['f24']
        rawhide.return_value = 'f24'

        # Mock out koji results
        container_build = {
            'build_id': 'fake_build_id',
            'name': 'cockpit', 'version': 1, 'release': 2, 'arch': 'foo',
        }
        rpm_build = {
            'build_id': 'fake_build_id',
            'name': 'guake', 'version': 1, 'release': 2, 'arch': 'foo',
        }
        get_build.return_value = container_build
        builds.return_value = [container_build]
        archives.return_value = [{
            'build_id': 802427,
            'buildroot_id': 6459519,
            'checksum': 'bf81b182dfbbf331ddd5700327abb4fe',
            'checksum_type': 0,
            'extra': 'stuff goes here...',
            'filename': 'docker-image-e3be590239f.x86_64.tar.gz',
            'id': 14707,
            'metadata_only': False,
            'size': 199457398,
            'type_description': 'Tar files',
            'type_extensions': 'tar tar.gz tar.bz2 tar.xz',
            'type_id': 4,
            'type_name': 'tar'}
        ]
        rpms.return_value = [rpm_build]

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-component-relationships': [
                ('GET', {
                    'page': 1,
                    'from_component_release': 'fedora-24-updates',
                    'type': 'ContainerIncludesRPM',
                }),
                ('GET', {
                    'page': 1,
                    'from_component_release': 'fedora-24-updates',
                    'type': 'ContainerIncludesRPM',
                }),
            ],
            'releases/fedora-24-updates': [('GET', {}), ('GET', {})]
        })

        # Check the results.
        self.assertSetEqual(present, set([]))
        self.assertSetEqual(absent, set([
            'cockpit/fedora-24-updates ContainerIncludesRPM guake/fedora-24-updates',
        ]))
