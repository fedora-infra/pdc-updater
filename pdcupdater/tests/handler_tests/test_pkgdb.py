import json
import mock

from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)

PKGDB_DATA = json.loads('''
{
  "output": "ok",
  "packages": [
    {
      "acls": [
        {
          "acls": ["..."],
          "collection": {
            "allow_retire": true,
            "branchname": "master",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".fc24",
            "koji_name": "rawhide",
            "name": "Fedora",
            "status": "Under Development",
            "version": "devel"
          },
          "critpath": false,
          "point_of_contact": "pingou",
          "status": "Approved",
          "status_change": 1400071464.0
        },
        {
          "acls": ["..."],
          "collection": {
            "allow_retire": false,
            "branchname": "el6",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".el6",
            "koji_name": "dist-6E-epel",
            "name": "Fedora EPEL",
            "status": "Active",
            "version": "6"
          },
          "critpath": false,
          "point_of_contact": "pingou",
          "status": "Approved",
          "status_change": 1400071051.0
        },
        {
          "acls": ["..."],
          "collection": {
            "allow_retire": false,
            "branchname": "f20",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".fc20",
            "koji_name": "f20",
            "name": "Fedora",
            "status": "EOL",
            "version": "20"
          },
          "critpath": false,
          "point_of_contact": "pingou",
          "status": "Approved",
          "status_change": 1427210598.0
        },
        {
          "acls": ["..."],
          "collection": {
            "allow_retire": false,
            "branchname": "epel7",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".el7",
            "koji_name": "epel7",
            "name": "Fedora EPEL",
            "status": "Active",
            "version": "7"
          },
          "critpath": false,
          "point_of_contact": "pingou",
          "status": "Approved",
          "status_change": 1433185353.0
        },
        {
          "acls": ["..."],
          "collection": {
            "allow_retire": false,
            "branchname": "f21",
            "date_created": "2014-07-08 18:02:03",
            "date_updated": "2014-07-08 18:02:03",
            "dist_tag": ".fc21",
            "koji_name": "f21",
            "name": "Fedora",
            "status": "Active",
            "version": "21"
          },
          "critpath": false,
          "point_of_contact": "pingou",
          "status": "Approved",
          "status_change": 1404852308.0
        },
        {
          "acls": ["..."],
          "collection": {
            "allow_retire": false,
            "branchname": "f22",
            "date_created": "2015-02-10 14:00:01",
            "date_updated": "2015-02-10 14:00:01",
            "dist_tag": ".fc22",
            "koji_name": "f22",
            "name": "Fedora",
            "status": "Active",
            "version": "22"
          },
          "critpath": false,
          "point_of_contact": "pingou",
          "status": "Approved",
          "status_change": 1423586678.0
        },
        {
          "acls": ["..."],
          "collection": {
            "allow_retire": false,
            "branchname": "f23",
            "date_created": "2015-07-14 18:13:12",
            "date_updated": "2015-07-14 18:13:12",
            "dist_tag": ".fc23",
            "koji_name": "f23",
            "name": "Fedora",
            "status": "Active",
            "version": "23"
          },
          "critpath": false,
          "point_of_contact": "pingou",
          "status": "Approved",
          "status_change": 1436906709.0
        }
      ],
      "creation_date": 1400070978.0,
      "description": "Guake is a drop-down terminal for Gnome Desktop",
      "koschei_monitor": false,
      "monitor": true,
      "name": "guake",
      "review_url": null,
      "status": "Approved",
      "summary": "Drop-down terminal for GNOME",
      "upstream_url": "http://www.guake.org/"
    },
    {
      "acls": [
        {
          "acls": ["..."],
          "collection": {
            "allow_retire": true,
            "branchname": "master",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".fc24",
            "koji_name": "rawhide",
            "name": "Fedora",
            "status": "Under Development",
            "version": "devel"
          },
          "critpath": false,
          "point_of_contact": "josef",
          "status": "Approved",
          "status_change": 1400071155.0
        },
        {
          "acls": ["..."],
          "collection": {
            "allow_retire": false,
            "branchname": "el6",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".el6",
            "koji_name": "dist-6E-epel",
            "name": "Fedora EPEL",
            "status": "Active",
            "version": "6"
          },
          "critpath": false,
          "point_of_contact": "josef",
          "status": "Approved",
          "status_change": 1400071054.0
        },
        {
          "acls": ["..."],
          "collection": {
            "allow_retire": false,
            "branchname": "epel7",
            "date_created": "2014-05-14 12:36:15",
            "date_updated": "2014-05-14 12:36:15",
            "dist_tag": ".el7",
            "koji_name": "epel7",
            "name": "Fedora EPEL",
            "status": "Active",
            "version": "7"
          },
          "critpath": false,
          "point_of_contact": "josef",
          "status": "Approved",
          "status_change": 1400071867.0
        },
        {
          "acls": ["..."],
          "collection": {
            "allow_retire": false,
            "branchname": "f23",
            "date_created": "2015-07-14 18:13:12",
            "date_updated": "2015-07-14 18:13:12",
            "dist_tag": ".fc23",
            "koji_name": "f23",
            "name": "Fedora",
            "status": "Active",
            "version": "23"
          },
          "critpath": false,
          "point_of_contact": "josef",
          "status": "Approved",
          "status_change": 1436899104.0
        }
      ],
      "creation_date": 1400070978.0,
      "description": "Geany is a small and fast integrated development enviroment",
      "koschei_monitor": true,
      "monitor": true,
      "name": "geany",
      "review_url": null,
      "status": "Approved",
      "summary": "A fast and lightweight IDE using GTK2",
      "upstream_url": "http://www.geany.org/"
    }
  ],
  "page": 1,
  "page_total": 1
}
''')



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

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb')
    def test_initialize_new_package(self, pdc, pkgdb):
        # Mock out FAS results
        pkgdb.return_value = PKGDB_DATA['packages']

        # Call the initializer
        self.handler.initialize(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'global-components': [
                ('POST', [
                    dict(
                        name='guake',
                    ),
                    dict(
                        name='geany',
                    ),
                ]),
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

    @mock_pdc
    @mock.patch('pdcupdater.services.pkgdb')
    def test_initialize_new_package_branch(self, pdc, pkgdb):
        # Mock out FAS results
        pkgdb.return_value = PKGDB_DATA['packages']

        # Call the initializer
        self.handler.initialize(pdc)

        # Check the PDC calls..
        self.assertDictEqual(pdc.calls, {
            'release-components': [
                ('POST', [
                  {'active': True,
                   'brew_package': u'guake',
                   'bugzilla_component': u'guake',
                   'dist_git_branch': u'master',
                   'global_component': u'guake',
                   'name': u'guake',
                   'release': u'rawhide',
                   'type': 'srpm'},
                  {'active': True,
                   'brew_package': u'guake',
                   'bugzilla_component': u'guake',
                   'dist_git_branch': u'el6',
                   'global_component': u'guake',
                   'name': u'guake',
                   'release': u'dist-6E-epel',
                   'type': 'srpm'},
                  {'active': True,
                   'brew_package': u'guake',
                   'bugzilla_component': u'guake',
                   'dist_git_branch': u'f20',
                   'global_component': u'guake',
                   'name': u'guake',
                   'release': u'f20',
                   'type': 'srpm'},
                  {'active': True,
                   'brew_package': u'guake',
                   'bugzilla_component': u'guake',
                   'dist_git_branch': u'epel7',
                   'global_component': u'guake',
                   'name': u'guake',
                   'release': u'epel7',
                   'type': 'srpm'},
                  {'active': True,
                   'brew_package': u'guake',
                   'bugzilla_component': u'guake',
                   'dist_git_branch': u'f21',
                   'global_component': u'guake',
                   'name': u'guake',
                   'release': u'f21',
                   'type': 'srpm'},
                  {'active': True,
                   'brew_package': u'guake',
                   'bugzilla_component': u'guake',
                   'dist_git_branch': u'f22',
                   'global_component': u'guake',
                   'name': u'guake',
                   'release': u'f22',
                   'type': 'srpm'},
                  {'active': True,
                   'brew_package': u'guake',
                   'bugzilla_component': u'guake',
                   'dist_git_branch': u'f23',
                   'global_component': u'guake',
                   'name': u'guake',
                   'release': u'f23',
                   'type': 'srpm'},
                  {'active': True,
                   'brew_package': u'geany',
                   'bugzilla_component': u'geany',
                   'dist_git_branch': u'master',
                   'global_component': u'geany',
                   'name': u'geany',
                   'release': u'rawhide',
                   'type': 'srpm'},
                  {'active': True,
                   'brew_package': u'geany',
                   'bugzilla_component': u'geany',
                   'dist_git_branch': u'el6',
                   'global_component': u'geany',
                   'name': u'geany',
                   'release': u'dist-6E-epel',
                   'type': 'srpm'},
                  {'active': True,
                   'brew_package': u'geany',
                   'bugzilla_component': u'geany',
                   'dist_git_branch': u'epel7',
                   'global_component': u'geany',
                   'name': u'geany',
                   'release': u'epel7',
                   'type': 'srpm'},
                  {'active': True,
                   'brew_package': u'geany',
                   'bugzilla_component': u'geany',
                   'dist_git_branch': u'f23',
                   'global_component': u'geany',
                   'name': u'geany',
                   'release': u'f23',
                   'type': 'srpm'},
                ]),
            ],
        })
