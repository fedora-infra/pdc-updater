import copy
import mock

import pdcupdater.utils
from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)

PKGDB_DATA = [
    {
        "collections": [{
            "allow_retire": True,
            "branchname": "master",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".fc24",
            "koji_name": "rawhide",
            "name": "Fedora",
            "status": "Under Development",
            "version": "devel"
        }, {
            "allow_retire": False,
            "branchname": "el6",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".el6",
            "koji_name": "dist-6E-epel",
            "name": "Fedora EPEL",
            "status": "Active",
            "version": "6"
        }, {
            "allow_retire": False,
            "branchname": "f20",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".fc20",
            "koji_name": "f20",
            "name": "Fedora",
            "status": "EOL",
            "version": "20"
        }, {
            "allow_retire": False,
            "branchname": "epel7",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".el7",
            "koji_name": "epel7",
            "name": "Fedora EPEL",
            "status": "Active",
            "version": "7"
        }, {
            "allow_retire": False,
            "branchname": "f21",
            "date_created": "2014-07-08 18:02:03",
            "date_updated": "2014-07-08 18:02:03",
            "dist_tag": ".fc21",
            "koji_name": "f21",
            "name": "Fedora",
            "status": "Active",
            "version": "21"
        }, {
            "allow_retire": False,
            "branchname": "f22",
            "date_created": "2015-02-10 14:00:01",
            "date_updated": "2015-02-10 14:00:01",
            "dist_tag": ".fc22",
            "koji_name": "f22",
            "name": "Fedora",
            "status": "Active",
            "version": "22"
        }, {
            "allow_retire": False,
            "branchname": "f23",
            "date_created": "2015-07-14 18:13:12",
            "date_updated": "2015-07-14 18:13:12",
            "dist_tag": ".fc23",
            "koji_name": "f23",
            "name": "Fedora",
            "status": "Active",
            "version": "23"
        }],
        "creation_date": 1400070978.0,
        "description": "Guake is a drop-down terminal for Gnome Desktop",
        "koschei_monitor": False,
        "monitor": True,
        "name": "guake",
        "review_url": None,
        "status": "Approved",
        "summary": "Drop-down terminal for GNOME",
        "upstream_url": "http://www.guake.org/"
    }, {

        "collections": [{
            "allow_retire": True,
            "branchname": "master",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".fc24",
            "koji_name": "rawhide",
            "name": "Fedora",
            "status": "Under Development",
            "version": "devel"
          }, {
            "allow_retire": False,
            "branchname": "el6",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".el6",
            "koji_name": "dist-6E-epel",
            "name": "Fedora EPEL",
            "status": "Active",
            "version": "6"
          }, {
            "allow_retire": False,
            "branchname": "epel7",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".el7",
            "koji_name": "epel7",
            "name": "Fedora EPEL",
            "status": "Active",
            "version": "7"
          }, {
            "allow_retire": False,
            "branchname": "f23",
            "date_created": "2015-07-14 18:13:12",
            "date_updated": "2015-07-14 18:13:12",
            "dist_tag": ".fc23",
            "koji_name": "f23",
            "name": "Fedora",
            "status": "Active",
            "version": "23"
          }],
        "creation_date": 1400070978.0,
        "description": "Geany is a small and fast integrated development enviroment",
        "koschei_monitor": True,
        "monitor": True,
        "name": "geany",
        "review_url": None,
        "status": "Approved",
        "summary": "A fast and lightweight IDE using GTK2",
        "upstream_url": "http://www.geany.org/"
    }
    ]

PDC_DATA = [
    {
        'active': True,
        'brew_package': u'guake',
        #'bugzilla_component': u'guake',
        'dist_git_branch': u'master',
        'global_component': u'guake',
        'name': u'guake',
        'release': u'fedora-24',
        'type': 'rpm'
    },
    {
        'active': True,
        'brew_package': u'guake',
        #'bugzilla_component': u'guake',
        'dist_git_branch': u'el6',
        'global_component': u'guake',
        'name': u'guake',
        'release': u'epel-6-updates',
        'type': 'rpm'
    },
    {
        'active': True,
        'brew_package': u'guake',
        #'bugzilla_component': u'guake',
        'dist_git_branch': u'f20',
        'global_component': u'guake',
        'name': u'guake',
        'release': u'fedora-20-updates',
        'type': 'rpm'
    },
    {
        'active': True,
        'brew_package': u'guake',
        #'bugzilla_component': u'guake',
        'dist_git_branch': u'epel7',
        'global_component': u'guake',
        'name': u'guake',
        'release': u'epel-7-updates',
        'type': 'rpm'
    },
    {
        'active': True,
        'brew_package': u'guake',
        #'bugzilla_component': u'guake',
        'dist_git_branch': u'f21',
        'global_component': u'guake',
        'name': u'guake',
        'release': u'fedora-21-updates',
        'type': 'rpm'
    },
    {
        'active': True,
        'brew_package': u'guake',
        #'bugzilla_component': u'guake',
        'dist_git_branch': u'f22',
        'global_component': u'guake',
        'name': u'guake',
        'release': u'fedora-22-updates',
        'type': 'rpm'
    },
    {
        'active': True,
        'brew_package': u'guake',
        #'bugzilla_component': u'guake',
        'dist_git_branch': u'f23',
        'global_component': u'guake',
        'name': u'guake',
        'release': u'fedora-23-updates',
        'type': 'rpm'
    },
    {
        'active': True,
        'brew_package': u'geany',
        #'bugzilla_component': u'geany',
        'dist_git_branch': u'master',
        'global_component': u'geany',
        'name': u'geany',
        'release': u'fedora-24',
        'type': 'rpm'
    },
    {
        'active': True,
        'brew_package': u'geany',
        #'bugzilla_component': u'geany',
        'dist_git_branch': u'el6',
        'global_component': u'geany',
        'name': u'geany',
        'release': u'epel-6-updates',
        'type': 'rpm'
    },
    {
        'active': True,
        'brew_package': u'geany',
        #'bugzilla_component': u'geany',
        'dist_git_branch': u'epel7',
        'global_component': u'geany',
        'name': u'geany',
        'release': u'epel-7-updates',
        'type': 'rpm'
    },
    {
        'active': True,
        'brew_package': u'geany',
        #'bugzilla_component': u'geany',
        'dist_git_branch': u'f23',
        'global_component': u'geany',
        'name': u'geany',
        'release': u'fedora-23-updates',
        'type': 'rpm'
    }
    ]



class TestNewPackage(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.pkgdb:NewPackageHandler'
    config = {}

    def test_cannot_handle_fedbadges(self):
        idx = '2015-6c98c8e3-0dcb-497d-a0d8-0b3d026a4cfb'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    def test_cannot_handle_bodhi(self):
        idx = '2015-9045593c-7376-43e8-af15-dc4c3fadc1f5'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    def test_cannot_handle_pkgdb_new_branch(self):
        idx = '2015-fc7a1d4f-56d8-45d6-a780-b317f0033a16'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    def test_can_handle_pkgdb_new_package(self):
        idx = '2015-5affaacc-1539-4e4f-9a5c-5b3f5c7caccf'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, True)

    @mock_pdc
    def test_handle_new_package(self, pdc):
        idx = '2015-5affaacc-1539-4e4f-9a5c-5b3f5c7caccf'
        msg = pdcupdater.utils.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        self.assertDictEqual(pdc.calls, {
            'releases/fedora-23-updates': [
                ('GET', dict()),
            ],
            'global-components': [
                ('GET', dict(name=u'perl-Lingua-Translit')),
            ],
            'release-components': [
                ('POST', dict(
                    name=u'perl-Lingua-Translit',
                    global_component=u'perl-Lingua-Translit',
                    #bugzilla_component=u'perl-Lingua-Translit',
                    brew_package=u'perl-Lingua-Translit',
                    release='fedora-23-updates',
                    dist_git_branch=u'f23',
                    type='rpm',
                    active=True,
                )),
            ],
        })

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb_packages')
    def test_audit_simple(self, pdc, pkgdb):
        # Mock out pgkdb results
        pkgdb.return_value = PKGDB_DATA

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'global-components': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb_packages')
    def test_audit_with_an_extra(self, pdc, pkgdb):
        # Mock out pgkdb results
        pkgdb.return_value = copy.deepcopy(PKGDB_DATA)
        del(pkgdb.return_value[0])

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'global-components': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set(['guake']))
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb_packages')
    def test_audit_missing_one(self, pdc, pkgdb):
        # Mock out pgkdb results
        pkgdb.return_value = copy.deepcopy(PKGDB_DATA)
        pkg = {
            "name": "gnome-terminal",
            "review_url": None,
            "status": "Approved",
            "summary": "The gnome terminal",
            "upstream_url": "http://www.gnome.org/"
        }
        pkgdb.return_value.append(pkg)

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'global-components': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set(['gnome-terminal']))

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb_packages')
    def test_audit_flipping_out(self, pdc, pkgdb):
        # Mock out pgkdb results
        pkgdb.return_value = copy.deepcopy(PKGDB_DATA)
        pkg = {
            "name": "gnome-terminal",
            "review_url": None,
            "status": "Approved",
            "summary": "The gnome terminal",
            "upstream_url": "http://www.gnome.org/"
        }
        del(pkgdb.return_value[0])
        pkgdb.return_value.append(pkg)

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'global-components': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set(['guake']))
        self.assertSetEqual(absent, set([('gnome-terminal')]))

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb_packages')
    def test_initialize_new_package(self, pdc, pkgdb):
        # Mock out pgkdb results
        pkgdb.return_value = PKGDB_DATA

        # Call the initializer
        self.handler.initialize(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'global-components': [
                ('POST', dict(
                    name='guake',
                )),
                ('POST', dict(
                    name='geany',
                )),
            ],
        })


class TestNewBranch(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.pkgdb:NewPackageBranchHandler'
    config = {}

    def test_can_handle_pkgdb_new_branch(self):
        idx = '2015-fc7a1d4f-56d8-45d6-a780-b317f0033a16'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, True)

    def test_cannot_handle_pkgdb_new_package(self):
        idx = '2015-5affaacc-1539-4e4f-9a5c-5b3f5c7caccf'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertEquals(result, False)

    @mock_pdc
    def test_handle_new_package_branch(self, pdc):
        idx = '2015-fc7a1d4f-56d8-45d6-a780-b317f0033a16'
        msg = pdcupdater.utils.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        self.assertDictEqual(pdc.calls, {
            'release-components': [
                ('POST', dict(
                    name=u'perl-Lingua-Translit',
                    global_component=u'perl-Lingua-Translit',
                    #bugzilla_component=u'perl-Lingua-Translit',
                    brew_package=u'perl-Lingua-Translit',
                    release='fedora-24',
                    dist_git_branch=u'master',
                    type='rpm',
                    active=True,
                )),
            ],
            'releases/fedora-24': [('GET', {})],
            'global-components': [('GET', {'name': u'perl-Lingua-Translit'}) ],
        })

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb_packages')
    def test_audit_simple(self, pdc, pkgdb):
        # Mock out pgkdb results
        pkgdb.return_value = PKGDB_DATA

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-components': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb_packages')
    def test_audit_with_an_extra(self, pdc, pkgdb):
        # Mock out pgkdb results
        pkgdb.return_value = copy.deepcopy(PKGDB_DATA)
        del(pkgdb.return_value[0]['collections'][0])

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-components': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set([('guake', 'fedora-24', 'master')]))
        self.assertSetEqual(absent, set())

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb_packages')
    def test_audit_missing_one(self, pdc, pkgdb):
        # Mock out pgkdb results
        pkgdb.return_value = copy.deepcopy(PKGDB_DATA)
        collection = {
            "allow_retire": True,
            "branchname": "f18",
            "dist_tag": ".fc18",
            "koji_name": "dist-f18",
            "name": "Fedora",
            "status": "EOL",
            "version": "18"
        }
        pkgdb.return_value[0]['collections'].append(collection)

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-components': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set())
        self.assertSetEqual(absent, set([('guake', 'fedora-18-updates', 'f18')]))

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb_packages')
    def test_audit_flipping_out(self, pdc, pkgdb):
        # Mock out pgkdb results
        pkgdb.return_value = copy.deepcopy(PKGDB_DATA)
        collection = {
            "allow_retire": True,
            "branchname": "f18",
            "dist_tag": ".fc18",
            "koji_name": "dist-f18",
            "name": "Fedora",
            "status": "EOL",
            "version": "18"
        }
        del(pkgdb.return_value[0]['collections'][0])
        pkgdb.return_value[0]['collections'].append(collection)

        # Call the auditor
        present, absent = self.handler.audit(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-components': [
                ('GET', {'page': 1}),
            ],
        })

        # Check the results.
        self.assertSetEqual(present, set([('guake', 'fedora-24', 'master')]))
        self.assertSetEqual(absent, set([('guake', 'fedora-18-updates', 'f18')]))

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb_packages')
    def test_initialize_new_package_branch(self, pdc, pkgdb):
        # Mock out pgkdb results
        pkgdb.return_value = PKGDB_DATA

        # Call the initializer
        self.handler.initialize(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-components': [
                ('POST', item) for item in PDC_DATA
            ],
            'releases/epel-6-updates': [('GET', {}), ('GET', {})],
            'releases/epel-7-updates': [('GET', {}), ('GET', {})],
            'releases/fedora-20-updates': [('GET', {})],
            'releases/fedora-21-updates': [('GET', {})],
            'releases/fedora-22-updates': [('GET', {})],
            'releases/fedora-23-updates': [('GET', {}), ('GET', {})],
            'releases/fedora-24': [('GET', {}), ('GET', {})],
        })
