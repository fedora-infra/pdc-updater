import logging
from datetime import datetime

import pdcupdater.services

log = logging.getLogger(__name__)


class RetireComponentHandler(pdcupdater.handlers.BaseHandler):
    """ When a component's branch is retired, EOL all it's branches """

    @property
    def topic_suffixes(self):
        return ['git.receive']

    def can_handle(self, pdc, msg):
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
        log.info("Retiring {type}/{global_component}#{name}".format(**branch))
        today = datetime.utcnow().date()
        for sla in branch['slas']:
            sla_eol = datetime.strptime(sla['eol'], '%Y-%m-%d').date()
            if sla_eol > today:
                pdc['component-branch-slas'][sla['id']]._ \
                    += {'eol': str(today)}

    def audit(self, pdc):
        pass

    def initialize(self, pdc):
        pass
