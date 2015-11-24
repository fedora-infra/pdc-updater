from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)


class TestNewPackage(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.pkgdb:NewPackageHandler'
    config = {}

    def test_cannot_handle_fedbadges(self):
        idx = '2015-6c98c8e3-0dcb-497d-a0d8-0b3d026a4cfb'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_cannot_handle_bodhi(self):
        idx = '2015-9045593c-7376-43e8-af15-dc4c3fadc1f5'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_cannot_handle_pkgdb_new_branch(self):
        idx = '2015-fc7a1d4f-56d8-45d6-a780-b317f0033a16'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_can_handle_pkgdb_new_package(self):
        idx = '2015-5affaacc-1539-4e4f-9a5c-5b3f5c7caccf'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, True)

    @mock_pdc
    def test_handle_new_package(self, pdc):
        idx = '2015-5affaacc-1539-4e4f-9a5c-5b3f5c7caccf'
        msg = self.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        self.assertDictEqual(pdc.calls, {
            'global-components': [
                ('POST', dict(name=u'perl-Lingua-Translit')),
            ],
            'release-components': [
                ('POST', dict(
                    name=u'perl-Lingua-Translit',
                    global_component=u'perl-Lingua-Translit',
                    bugzilla_component=u'perl-Lingua-Translit',
                    brew_package=u'perl-Lingua-Translit',
                    release=u'f23',
                    dist_git_branch=u'f23',
                    type='srpm',
                    active=True,
                )),
            ],
        })


class TestNewBranch(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.pkgdb:NewPackageBranchHandler'
    config = {}

    def test_can_handle_pkgdb_new_branch(self):
        idx = '2015-fc7a1d4f-56d8-45d6-a780-b317f0033a16'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, True)

    def test_cannot_handle_pkgdb_new_package(self):
        idx = '2015-5affaacc-1539-4e4f-9a5c-5b3f5c7caccf'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    @mock_pdc
    def test_handle_new_package_branch(self, pdc):
        idx = '2015-fc7a1d4f-56d8-45d6-a780-b317f0033a16'
        msg = self.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        self.assertDictEqual(pdc.calls, {
            'release-components': [
                ('POST', dict(
                    name=u'perl-Lingua-Translit',
                    global_component=u'perl-Lingua-Translit',
                    bugzilla_component=u'perl-Lingua-Translit',
                    brew_package=u'perl-Lingua-Translit',
                    release=u'rawhide',
                    dist_git_branch=u'master',
                    type='srpm',
                    active=True,
                )),
            ],
        })
