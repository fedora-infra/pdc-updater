import os
import shutil
import tarfile
import copy

from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)


class TestModuleStateChange(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.modules:ModuleStateChangeHandler'

    test_data_dir = os.path.join(os.path.dirname(__file__), "test_modules_data")
    modulemd_file = os.path.join(test_data_dir, "modulemd.yaml")
    with open(modulemd_file) as f:
        modulemd_example = f.read()
    repo_dir = os.path.join(test_data_dir, "repos")
    foo_repo_tar = os.path.join(repo_dir, "foo.tar")
    foo_repo_dir = os.path.join(repo_dir, "foo")
    foo_repo_url = foo_repo_dir + '?#286f3a32f3e034508012fcbba63ed40092e4129b'
    test_tree_dir = os.path.join(test_data_dir, "trees/Test-0-20160712.0")

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
        'state_name': 'done',
        'topdir': test_tree_dir
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
    def test_handle_created_tree(self, pdc):
        self.handler.handle(pdc, self.state_done_msg)
