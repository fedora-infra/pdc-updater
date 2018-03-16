import logging
from datetime import datetime
import requests

import pdcupdater.services
import pdcupdater.utils

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
        component_type = self._namespace_to_pdc(namespace)
        checkurl = self.config.get('pdcupdater.file_check_url')
        if not checkurl:
            log.error('No check URL configured, ignoring')
            return

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

        # Make sure that the file is still retired right this moment.
        # This fixes cases where people merge from master to an older branch, and one of the
        # intermediate commits contained a dead.package.
        fileurl = checkurl % {'namespace': namespace,
                              'repo': repo,
                              'branch': branch,
                              'file': 'dead.package'}
        log.info('Checking for file: %s' % fileurl)
        resp = requests.get(fileurl)
        if resp.status_code != 200:
            log.info('Seems not to actually be retired, possibly merge')
            return

        _retire_branch(pdc, branch)

    @staticmethod
    def _namespace_to_pdc(namespace):
        """ Internal method to translate a dist-git namespace to a PDC
        component type. """
        namespace_to_pdc = {
            'rpms': 'rpm',
            'modules': 'module',
            'container': 'container',
        }
        if namespace not in namespace_to_pdc:
            raise ValueError('The namespace "{0}" is not supported'
                             .format(namespace))
        else:
            return namespace_to_pdc[namespace]

    @staticmethod
    def _pdc_to_namespace(pdc_type):
        """ Internal method to translate a PDC component type to a dist-git
        namespace. """
        pdc_to_namespace = {
            'rpm': 'rpms',
            'module': 'modules',
            'container': 'container',
        }
        if pdc_type not in pdc_to_namespace:
            raise ValueError('The PDC type "{0}" is not supported'
                             .format(pdc_type))
        else:
            return pdc_to_namespace[pdc_type]

    def audit(self, pdc):
        """ Returns the difference in retirement status in PDC and dist-git.

        This function compares the status in PDC and the status in the
        "real world" (i.e., in dist-git) and return the difference.
        """
        branches_retired_in_distgit = set()
        branches_retired_in_pdc = set()
        session = requests.Session()

        log.info('Looking up all branches from PDC.')
        for branch in pdc.get_paged(pdc['component-branches']._):
            branch_str = '{type}/{global_component}#{name}'.format(**branch)
            log.debug('Considering {0}'.format(branch_str))
            retired_in_dist_git = _is_retired_in_dist_git(
                namespace=self._pdc_to_namespace(branch['type']),
                repo=branch['global_component'],
                branch=branch['name'],
                requests_session=session
            )

            if retired_in_dist_git:
                branches_retired_in_distgit.add(branch_str)
            if not branch['active']:
                branches_retired_in_pdc.add(branch_str)

        present = branches_retired_in_pdc - branches_retired_in_distgit
        absent = branches_retired_in_distgit - branches_retired_in_pdc

        return present, absent

    def initialize(self, pdc):
        """ Initialize PDC retirement status from analyzing dist-git.

        This steps over all the branches in dist-git and retires any branches
        in PDC that have a dead.package file in dist-git.
        """
        session = requests.Session()

        # Look up all non-retired branches from PDC
        log.info('Looking up active branches from PDC.')

        for branch in pdc.get_paged(pdc['component-branches']._, active=True):
            log.debug('Considering {type}/{global_component}#{name}'
                      .format(**branch))
            retired_in_dist_git = _is_retired_in_dist_git(
                namespace=self._pdc_to_namespace(branch['type']),
                repo=branch['global_component'],
                branch=branch['name'],
                requests_session=session
            )

            if retired_in_dist_git:
                _retire_branch(pdc, branch)

@pdcupdater.utils.retry(wait_on=requests.exceptions.ConnectionError)
def _is_retired_in_dist_git(namespace, repo, branch, requests_session=None):
    if requests_session is None:
        requests_session = requests.Session()

    base = 'https://src.fedoraproject.org/'
    # Check to see if they have a dead.package file in dist-git
    url = '{base}/{namespace}/{repo}/raw/{branch}/f/dead.package'
    response = requests_session.head(url.format(
        base=base,
        namespace=namespace,
        repo=repo,
        branch=branch,
    ))

    # If there is a dead.package, then the branch is retired in dist_git
    if response.status_code in [200, 404]:
        return response.status_code == 200
    else:
        raise ValueError(
            'The connection to dist_git failed. Retirement status could not '
            'be determined. The status code was: {0}. The content was: '
            '{1}'.format(response.status_code, response.content))


@pdcupdater.utils.retry(wait_on=requests.exceptions.ConnectionError)
def _retire_branch(pdc, branch):
    """ Internal method for retiring a branch in PDC. """
    today = datetime.utcnow().date()
    for sla in branch['slas']:
        sla_eol = datetime.strptime(sla['eol'], '%Y-%m-%d').date()
        if sla_eol > today:
            pdc['component-branch-slas'][sla['id']]._ \
                += {'eol': str(today)}
