import logging
from datetime import datetime

import requests
import pdcupdater.services

log = logging.getLogger(__name__)


class RetireComponentHandler(pdcupdater.handlers.BaseHandler):
    """ When a component's branch is retired, EOL all SLAs on that branch.  """

    @property
    def topic_suffixes(self):
        return ['git.receive']

    def can_handle(self, pdc, msg):
        """ Return true if this handler can/should handle a message. """
        if not msg['topic'].endswith('git.receive'):
            return False

        # If there is no dead.package in the commit, then it can be ignored
        if 'dead.package' not in msg['msg']['commit']['stats']['files']:
            return False

        dead_package_commit = \
            msg['msg']['commit']['stats']['files']['dead.package']
        # Only handles the message if the dead.package was added, not deleted
        return dead_package_commit['additions'] > 0 \
            and dead_package_commit['deletions'] == 0

    def handle(self, pdc, msg):
        """ Handle an incoming bus message.

        The message should be a dist-git retirement message (where someone adds
        a dead.package file to the repo).  In response, this method will retire
        the package in PDC.
        """
        branch = msg['msg']['commit']['branch']
        repo = msg['msg']['commit']['repo']
        namespace = msg['msg']['commit']['namespace']
        # The dist-git namespaces are plural but the types are singular in PDC
        if namespace.endswith('s'):
            component_type = namespace[:-1]
        else:
            component_type = namespace
        # This query guarantees a unique component branch, so a count of 1 is
        # expected
        branch_query_rv = pdc['component-branches']._(
            name=branch, type=component_type, global_component=repo)

        if branch_query_rv['count'] != 1:
            log.error('"{0}/{1}" was not found in PDC'.format(namespace, repo))
            return

        branch = branch_query_rv['results'][0]
        # If the branch is already EOL in PDC, don't do anything
        if branch['active'] is False:
            return

        self._retire_branch(pdc, branch)

    @staticmethod
    def _retire_branch(pdc, branch):
        """ Internal method for retiring a branch in PDC. """
        log.info("Retiring {type}/{global_component}#{name}".format(**branch))
        today = datetime.utcnow().date()
        for sla in branch['slas']:
            sla_eol = datetime.strptime(sla['eol'], '%Y-%m-%d').date()
            if sla_eol > today:
                pdc['component-branch-slas'][sla['id']]._ \
                    += {'eol': str(today)}

    def audit(self, pdc):
        """ Not Implemented.

        This function (if it were implemented) should compare the status in PDC
        and the status in the "real world" (i.e., in dist-git) and return the
        difference.
        """
        pass

    def initialize(self, pdc):
        """ Initialize PDC retirement status from analyzing dist-git.

        This steps over all the branches in dist-git and retires any branches
        in PDC that have a dead.package file in dist-git.
        """
        session = requests.Session()
        cgit_url = "https://src.fedoraproject.org/cgit"
        pdc2namespace = {
            'rpm': 'rpms',
            'module': 'modules',
            'container': 'container',
        }

        # Look up all non-retired branches from PDC
        log.info("Looking up active branches from PDC.")
        branches = pdc.get_paged(pdc['component-branches'], active=True)

        for branch in branches:
            log.debug("Considering {type}/{global_component}#{name}".format(**branch))
            # Check to see if they have a dead.package file in dist-git
            url = "{base}/{type}/{repo}.git/plain/dead.package?h={branch}"
            response = session.head(url.format(
                base=cgit_url,
                type=pdc2namespace[branch['type']],
                repo=branch['global_component'],
                branch=branch['name'],
            ))

            # If so, then we need to retire them.
            if bool(response):
                self._retire_branch(pdc, branch)
