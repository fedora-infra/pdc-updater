import os
import shutil
import tarfile
import copy
import mock

from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)

def mocked_koji_from_tag(url, tag):
    if tag != 'epel7':
        return []
    return [{
        'build_id': 698494,
        'name': 'dvisvgm',
        'arch': 'src',
        'buildtime': 1447252790,
        'id': 6979644,
        'epoch': None,
        'version': '1.11',
        'release': '1.el7',
        'buildroot_id': 4386200,
        'payloadhash': '46f384609c0db547753857d5b0476cae',
        'size': 841828,
        # Extracted from the associated build
        'srpm_name': 'dvisvgm',
    }, {
        'build_id': 698495,
        'name': 'dvisvgm2',
        'arch': 'src',
        'buildtime': 1447252790,
        'id': 6979645,
        'epoch': None,
        'version': '1.11',
        'release': '1.el7',
        'buildroot_id': 4386200,
        'payloadhash': '46f384609c0db547753857d5b0476cae',
        'size': 841828,
        # Extracted from the associated build
        'srpm_name': 'dvisvgm2',
    }, {
        'build_id': 696907,
        'name': 'rubygem-jmespath-doc',
        'arch': 'noarch',
        'buildtime': 1446997456,
        'id': 6968508,
        'epoch': None,
        'version': '1.1.3',
        'release': '1.el7',
        'buildroot_id': 4364114,
        'payloadhash': '6b98468f3efe29367c923c577861dec5',
        'size': 175000,
        # Extracted from the associated build
        'srpm_name': 'rubygem-jmespath',
        'srpm_nevra': 'rubygem-jmespath-1.1.3-1.el7',
    }]

class TestModuleStateChange(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.modules:ModuleStateChangeHandler'

    test_data_dir = os.path.join(os.path.dirname(__file__), "test_modules_data")
    modulemd_file = os.path.join(test_data_dir, "modulemd.yaml")
    with open(modulemd_file) as f:
        modulemd_example = f.read()
    modulemd_file = os.path.join(test_data_dir, "modulemd-minimal.yaml")
    with open(modulemd_file) as f:
        modulemd_minimal_example = f.read()
    repo_dir = os.path.join(test_data_dir, "repos")
    foo_repo_tar = os.path.join(repo_dir, "foo.tar")
    foo_repo_dir = os.path.join(repo_dir, "foo")
    foo_repo_url = foo_repo_dir + '?#286f3a32f3e034508012fcbba63ed40092e4129b'

    state_init_msg = {
        'topic': 'org.fedoraproject.stg.mbs.module.state.change',
        'msg': {
            'state': 0,
            'state_name': 'init',
            'name': 'core',
            'stream': '24',
            'version': '0',
            'scmurl': foo_repo_url,
            'modulemd': modulemd_example,
        }
    }

    state_done_msg = copy.deepcopy(state_init_msg)
    state_done_msg['topic'] = 'org.fedoraproject.stg.mbs.module.state.change'
    state_done_msg['msg'].update({
        'state': 3,
        'state_name': 'done'
    })

    def setUp(self):
        super(TestModuleStateChange, self).setUp()

        # Remove example repo that may be left over from previous calls.
        try:
            shutil.rmtree(self.foo_repo_dir)
        except OSError:
            pass

        # Untar example repository
        with tarfile.open(self.foo_repo_tar, "r") as tar:
            tar.extractall(self.repo_dir)

    def tearDown(self):
        super(TestModuleStateChange, self).tearDown()
        shutil.rmtree(self.foo_repo_dir)

    @mock_pdc
    def test_create_unreleased_variant(self, pdc):
        self.handler.handle(pdc, self.state_init_msg)

    @mock_pdc
    def test_update_unreleased_variant(self, pdc):
        self.handler.handle(pdc, self.state_done_msg)


    @mock_pdc
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_get_unreleased_variant_rpms(self, pdc, koji):
        koji.side_effect = mocked_koji_from_tag

        variant = {}
        variant["koji_tag"] = "epel7"
        variant["modulemd"] = self.modulemd_example

        expected_rpms = [
            {'epoch': 0, 'version': '1.11',
             'name': 'dvisvgm', 'release': '1.el7',
             'srpm_commit_hash': '76f9d8c8e87eed0aab91034b01d3d5ff6bd5b4cb',
             'srpm_commit_branch': 'f26', 'arch': 'src', 'srpm_name': 'dvisvgm'},
            {'epoch': 0, 'version': '1.11',
             'name': 'dvisvgm2', 'release': '1.el7',
             'srpm_commit_hash': '86f9d8c8e87eed0aab91034b01d3d5ff6bd5b4cb',
             'arch': 'src', 'srpm_name': 'dvisvgm2'},
            {'srpm_nevra': 'rubygem-jmespath-1.1.3-1.el7', 'epoch': 0,
             'version': '1.1.3', 'name': 'rubygem-jmespath-doc',
             'release': '1.el7', 'arch': 'noarch', 'srpm_name': 'rubygem-jmespath'}]
        rpms = self.handler.get_unreleased_variant_rpms(pdc, variant)
        self.assertEqual(expected_rpms, rpms)

    @mock_pdc
    @mock.patch('pdcupdater.services.koji_rpms_in_tag')
    def test_get_unreleased_variant_rpms_minimal_mmd(self, pdc, koji):
        koji.side_effect = mocked_koji_from_tag

        variant = {}
        variant["koji_tag"] = "epel7"
        variant["modulemd"] = self.modulemd_minimal_example

        expected_rpms = [
            {'epoch': 0, 'version': '1.11',
             'name': 'dvisvgm', 'release': '1.el7',
             'arch': 'src', 'srpm_name': 'dvisvgm'},
            {'epoch': 0, 'version': '1.11',
             'name': 'dvisvgm2', 'release': '1.el7',
             'arch': 'src', 'srpm_name': 'dvisvgm2'},
            {'srpm_nevra': 'rubygem-jmespath-1.1.3-1.el7', 'epoch': 0,
             'version': '1.1.3', 'name': 'rubygem-jmespath-doc',
             'release': '1.el7', 'arch': 'noarch', 'srpm_name': 'rubygem-jmespath'}]
        rpms = self.handler.get_unreleased_variant_rpms(pdc, variant)
        self.assertEqual(expected_rpms, rpms)
