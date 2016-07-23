import os
import shutil
import tarfile

from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)


class TestModuleStateChange(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.modules:ModuleStateChangeHandler'

    test_data_dir = os.path.join(os.path.dirname(__file__), "test_modules_data")
    repo_dir = os.path.join(test_data_dir, "repos")
    foo_repo_tar = os.path.join(repo_dir, "foo.tar")
    foo_repo_dir = os.path.join(repo_dir, "foo")
    foo_repo_url = foo_repo_dir + '?#286f3a32f3e034508012fcbba63ed40092e4129b'
    test_tree_dir = os.path.join(test_data_dir, "trees/Test-0-20160712.0")

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
    def test_handle_module(self, pdc):
        msg = {
            'topic': 'buildsys.module.state.change',
            'msg': {
                'state': 'done',
                'koji_tag': 'module-core-24',
                'module_uid': 'Core-24-0',
                'module_version': '24',
                'module_release': '0',
                'scmurl': self.foo_repo_url,
                'topdir': self.test_tree_dir,
            }
        }
        self.handler.handle(pdc, msg)
