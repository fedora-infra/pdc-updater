import pdcupdater.handlers
import pdcupdater.services
import pdcupdater.utils

import beanbag.bbexcept

import logging

log = logging.getLogger(__name__)


def collection2release_id(pdc, collection):
    # Silly rawhide.  We don't know what number you are...
    if collection['version'] == 'devel':
        collection['version'] = collection['dist_tag'].split('fc')[-1]
        release_type = 'ga'
        template = "{short}-{version}"
    else:
        release_type = 'updates'
        template = "{short}-{version}-updates"

    # lowercase this for the prefix.
    release = {
        'name': collection['name'],
        'short': collection['name'].lower().split()[-1],
        'version': collection['version'],
        'release_type': release_type,
    }
    release_id = template.format(**release)
    pdcupdater.utils.ensure_release_exists(pdc, release_id, release)
    return release_id


class NewPackageHandler(pdcupdater.handlers.BaseHandler):
    """ When a new package gets added to pkgdb. """

    def __init__(self, *args, **kwargs):
        super(NewPackageHandler, self).__init__(*args, **kwargs)
        self.pkgdb_url = self.config['pdcupdater.pkgdb_url']

    @property
    def topic_suffixes(self):
        return ['pkgdb.package.new']

    def can_handle(self, pdc, msg):
        return msg['topic'].endswith('pkgdb.package.new')

    def handle(self, pdc, msg):
        name = msg['msg']['package_name']
        branch = msg['msg']['package_listing']['collection']['branchname']
        collection = msg['msg']['package_listing']['collection']
        release_id = collection2release_id(pdc, collection)
        global_component = name
        data = dict(
            name=name,
            release=release_id,
            global_component=global_component,
            dist_git_branch=branch,
            #bugzilla_component=name,
            brew_package=name,
            active=True,
            type='rpm',
        )
        pdcupdater.utils.ensure_global_component_exists(pdc, name)
        # https://pdc.fedoraproject.org/rest_api/v1/release-components/
        log.info("Creating release component %s for %s" % (name, release_id))
        pdc['release-components']._(data)

    def audit(self, pdc):
        pkgdb_packages = pdcupdater.services.pkgdb_packages(self.pkgdb_url)
        pdc_packages = pdc.get_paged(pdc['global-components']._)

        # normalize the two lists
        pkgdb_packages = set([p['name'] for p in pkgdb_packages])
        pdc_packages = set([p['name'] for p in pdc_packages])

        # use set operators to determine the difference
        present = pdc_packages - pkgdb_packages
        absent = pkgdb_packages - pdc_packages

        return present, absent

    def initialize(self, pdc):
        packages = pdcupdater.services.pkgdb_packages(self.pkgdb_url)
        components = [dict(
            name=package['name'],
        ) for package in packages]
        for component in components:
            try:
                pdc['global-components']._(component)
            except beanbag.bbexcept.BeanBagException as e:
                log.warn("global-component, %r %r" % (component, e.response))


class NewPackageBranchHandler(pdcupdater.handlers.BaseHandler):
    """ When a new package gets a new branch in pkgdb. """

    def __init__(self, *args, **kwargs):
        super(NewPackageBranchHandler, self).__init__(*args, **kwargs)
        self.pkgdb_url = self.config['pdcupdater.pkgdb_url']

    @property
    def topic_suffixes(self):
        return ['pkgdb.package.branch.new']

    def can_handle(self, pdc, msg):
        return msg['topic'].endswith('pkgdb.package.branch.new')

    def handle(self, pdc, msg):
        name = msg['msg']['package_listing']['package']['name']
        branch = msg['msg']['package_listing']['collection']['branchname']
        collection = msg['msg']['package_listing']['collection']
        release_id = collection2release_id(pdc, collection)
        global_component = name
        data = dict(
            name=name,
            release=release_id,
            global_component=global_component,
            dist_git_branch=branch,
            #bugzilla_component=name,
            brew_package=name,
            active=True,
            type='rpm',
        )
        # https://pdc.fedoraproject.org/rest_api/v1/release-components/
        pdcupdater.utils.ensure_global_component_exists(pdc, name)
        log.info("Creating release component %s for %s" % (name, release_id))
        pdc['release-components']._(data)

    def audit(self, pdc):
        pkgdb_packages = pdcupdater.services.pkgdb_packages(
            self.pkgdb_url, extra=True)
        pdc_packages = pdc.get_paged(pdc['release-components']._)

        # normalize the two lists
        pkgdb_packages = set(
            (
                package['name'],
                pdcupdater.utils.pkgdb2release(collection),
                collection['branchname']
            )
            for package in pkgdb_packages
            for collection in package['collections']
        )
        pdc_packages = set(
            (p['name'], p['release']['release_id'], p['dist_git_branch'])
            for p in pdc_packages
        )

        # use set operators to determine the difference
        present = pdc_packages - pkgdb_packages
        absent = pkgdb_packages - pdc_packages

        return present, absent

    def initialize(self, pdc):
        packages = pdcupdater.services.pkgdb_packages(
            self.pkgdb_url, extra=True)
        components = [
            dict(
                name=package['name'],
                release=collection2release_id(pdc, collection),
                global_component=package['name'],
                dist_git_branch=collection['branchname'],
                #bugzilla_component=package['name'],
                brew_package=package['name'],
                active=True,
                type='rpm',
            )
        for package in packages
        for collection in package['collections']
        ]

        for component in components:
            try:
                pdc['release-components']._(component)
            except beanbag.bbexcept.BeanBagException as e:
                log.warn("release-component, %r %r" % (component, e.response))
