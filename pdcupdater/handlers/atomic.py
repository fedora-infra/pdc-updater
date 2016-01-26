import logging
import requests

import pdcupdater.handlers
import pdcupdater.services
import pdcupdater.utils

from pdc_client import get_paged


log = logging.getLogger(__name__)


class AtomicComponentGroupHandler(pdcupdater.handlers.BaseHandler):
    """ When someone changes the packages list for fedora-atomic.

    https://git.fedorahosted.org/cgit/fedora-atomic.git/tree/fedora-atomic-docker-host.json

    """
    group_type = 'atomic-docker-host'

    def __init__(self, *args, **kwargs):
        super(AtomicComponentGroupHandler, self).__init__(*args, **kwargs)
        self.git_url = self.config['pdcupdater.fedora_atomic_git_url']

    @property
    def topic_suffixes(self):
        return [
            'trac.git.receive',
        ]

    def can_handle(self, msg):
        if not msg['topic'].endswith('trac.git.receive'):
            return False
        if msg['msg']['commit']['repo'] != 'project-atomic':
            return False
        return True

    def atomic_component_group_from_git(self):
        # TODO -- handle mapping branches to releases.
        # for now we just do master <-> rawhide
        params = dict()  # use h=f23 for a different branch
        filename = 'fedora-%s.json' % self.group_type
        response = requests.get(self.git_url + filename, params=params)
        data = response.json()
        packages = data['packages']

        release_id = 'fedora-24' # XXX - hard-coded
        return {
            'group_type': self.group_type,
            'release': release_id,
            'description': 'Deps for %s %s' % (self.group_type, self.git_url),
            'components': [{
                'release': release_id,
                'name': package,
            } for package in packages],
        }

    def handle(self, pdc, msg):
        component_group = self.atomic_component_group_from_git()
        self._update_atomic_component_group(pdc, component_group)

    def audit(self, pdc):
        # Query the data sources
        git_group = self.atomic_component_group_from_git()
        pdc_groups = get_paged(pdc['component-groups']._)
        pdc_group = [
            group for group in pdc_groups
            if group['group_type'] == self.group_type
        ]

        # normalize the two lists
        git_group = set(git_group['components'])
        pdc_group = set(pdc_group['components'])

        # use set operators to determine the difference
        present = pdc_group - git_group
        absent = git_group - pdc_group

        return present, absent

    def initialize(self, pdc):
        component_group = self.atomic_component_group_from_git()
        self._update_atomic_component_group(pdc, component_group)

    def _update_atomic_component_group(self, pdc, component_group):
        # Figure out the primary key for this group we have here..
        group_pk = pdcupdater.utils.get_group_pk(pdc, component_group)

        # Make sure our pre-requisites exist
        pdcupdater.utils.ensure_component_group_exists(pdc, component_group)
        for component in component_group['components']:
            pdcupdater.utils.ensure_release_component_exists(
                pdc, component['release'], component['name'])

        # And perform the update with a PUT
        pdc['component-groups'][group_pk]._ = component_group
