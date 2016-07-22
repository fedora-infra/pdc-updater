import os

from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)


class TestNewTree(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.trees:NewTreeHandler'

    @mock_pdc
    def test_handle_new_tree(self, pdc):
        msg = {
            'topic': 'buildsys.module.state.change',
            'msg': {
                'state': 'done',
                'koji_tag': 'test-0',
                'module_uid': 'Test-0',
                'module_version': '0',
                'topdir': os.path.join(
                    os.path.dirname(__file__),
                    "test_trees_tree/Test-0-20160712.0/x86_64"),
            }
        }
        self.handler.handle(pdc, msg)
