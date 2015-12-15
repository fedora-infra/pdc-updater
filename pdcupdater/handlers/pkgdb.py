import pdcupdater.handlers
import pdcupdater.services

from pdc_client import get_paged


class NewPackageHandler(pdcupdater.handlers.BaseHandler):
    """ When a new package gets added to pkgdb. """

    def __init__(self, *args, **kwargs):
        super(NewPackageHandler, self).__init__(*args, **kwargs)
        self.pkgdb_url = self.config['pdcupdater.pkgdb_url']

    @property
    def topic_suffixes(self):
        return ['pkgdb.package.new']

    def can_handle(self, msg):
        return msg['topic'].endswith('pkgdb.package.new')

    def handle(self, pdc, msg):
        name = msg['msg']['package_name']
        branch = msg['msg']['package_listing']['collection']['branchname']
        release = msg['msg']['package_listing']['collection']['koji_name']
        global_component = name
        data = dict(
            name=name,
            release=release,
            global_component=global_component,
            dist_git_branch=branch,
            #bugzilla_component=name,
            brew_package=name,
            active=True,
            type='srpm',
        )
        # https://pdc.fedorainfracloud.org/rest_api/v1/global-components/
        pdc['global-components']._(dict(name=name))
        # https://pdc.fedorainfracloud.org/rest_api/v1/release-components/
        pdc['release-components']._(data)

    def audit(self, pdc):
        packages = pdcupdater.services.pkgdb_packages(self.pkgdb_url)
        pdc_pkgs = get_paged(pdc['global-components']._)

        # normalize the two lists
        pkg_package = set([p['name'] for p in packages])
        pdc_package = set([p['name'] for p in pdc_pkgs])

        # use set operators to determine the difference
        present = pdc_package - pkg_package
        absent = pkg_package - pdc_package

        return present, absent

    def initialize(self, pdc):
        packages = pdcupdater.services.pkgdb_packages(self.pkgdb_url)
        bulk_payload = [dict(
            name=package['name'],
        ) for package in packages]
        pdc['global-components']._(bulk_payload)


class NewPackageBranchHandler(pdcupdater.handlers.BaseHandler):
    """ When a new package gets a new branch in pkgdb. """

    def __init__(self, *args, **kwargs):
        super(NewPackageBranchHandler, self).__init__(*args, **kwargs)
        self.pkgdb_url = self.config['pdcupdater.pkgdb_url']

    @property
    def topic_suffixes(self):
        return ['pkgdb.package.branch.new']

    def can_handle(self, msg):
        return msg['topic'].endswith('pkgdb.package.branch.new')

    def handle(self, pdc, msg):
        name = msg['msg']['package_listing']['package']['name']
        branch = msg['msg']['package_listing']['collection']['branchname']
        release = msg['msg']['package_listing']['collection']['koji_name']
        global_component = name
        data = dict(
            name=name,
            release=release,
            global_component=global_component,
            dist_git_branch=branch,
            #bugzilla_component=name,
            brew_package=name,
            active=True,
            type='srpm',
        )
        # https://pdc.fedorainfracloud.org/rest_api/v1/release-components/
        pdc['release-components']._(data)

    def audit(self, pdc):
        packages = pdcupdater.services.pkgdb_packages(self.pkgdb_url, acls=True)
        pdc_pkgs = get_paged(pdc['release-components']._)

        # normalize the two lists
        pkg_package = set(
            (
                package['name'],
                acls['collection']['koji_name'],
                acls['collection']['branchname']
            )
            for package in packages
            for acls in package['acls']
        )
        pdc_package = set(
            (p['name'], p['release'], p['dist_git_branch'])
            for p in pdc_pkgs
        )

        # use set operators to determine the difference
        present = pdc_package - pkg_package
        absent = pkg_package - pdc_package

        return present, absent

    def initialize(self, pdc):
        packages = pdcupdater.services.pkgdb_packages(self.pkgdb_url, acls=True)
        bulk_payload = [
            dict(
                name=package['name'],
                release=acls['collection']['koji_name'],
                global_component=package['name'],
                dist_git_branch=acls['collection']['branchname'],
                #bugzilla_component=package['name'],
                brew_package=package['name'],
                active=True,
                type='srpm',
            )
        for package in packages
        for acls in package['acls']
        ]

        pdc['release-components']._(bulk_payload)
