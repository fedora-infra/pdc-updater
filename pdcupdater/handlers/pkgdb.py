import pdcupdater.handlers

class NewPackageHandler(pdcupdater.handlers.BaseHandler):
    """ When a new package gets added to pkgdb. """

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
            bugzilla_component=name,
            brew_package=name,
            active=True,
            type='srpm',
        )
        # https://pdc.fedorainfracloud.org/rest_api/v1/global-components/
        pdc['global-components']._(dict(name=name))
        # https://pdc.fedorainfracloud.org/rest_api/v1/release-components/
        pdc['release-components']._(data)

    def audit(self, pdc):
        raise NotImplementedError()

    def initialize(self, pdc):
        raise NotImplementedError()


class NewPackageBranchHandler(pdcupdater.handlers.BaseHandler):
    """ When a new package gets a new branch in pkgdb. """

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
            bugzilla_component=name,
            brew_package=name,
            active=True,
            type='srpm',
        )
        # https://pdc.fedorainfracloud.org/rest_api/v1/release-components/
        pdc['release-components']._(data)

    def audit(self, pdc):
        raise NotImplementedError()

    def initialize(self, pdc):
        raise NotImplementedError()
