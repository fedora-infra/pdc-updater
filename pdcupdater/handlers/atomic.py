import logging
import requests

import pdcupdater.handlers
import pdcupdater.services
import pdcupdater.utils


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

    def can_handle(self, pdc, msg):
        if not msg['topic'].endswith('trac.git.receive'):
            return False
        if msg['msg']['commit']['repo'] != 'fedora-atomic':
            return False
        return True

    def atomic_component_groups_from_git(self, pdc):
        # First, build a mapping of git branches (from the fedora-atomic
        # fedorahosted repo) to PDC release ids.
        tags = [pdcupdater.utils.rawhide_tag()]
        for release in pdcupdater.utils.bodhi_releases():
            if 'EPEL' in release['id_prefix']:
                # We don't maintain an atomic group for epel.
                continue
            tags.append(release['stable_tag'])

        pdc_releases = [pdcupdater.utils.tag2release(tag) for tag in tags]
        for release_id, release in pdc_releases:
            # First, make sure PDC can handle a group on this release
            pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

            # Then, map the fedorahosted git repo branch to our PDC release
            if release['release_type'] == 'ga':
                branch = 'master'
            else:
                branch = 'f' + release['version']

            # Go, get, and parse the data
            params = dict(h=branch)
            filename = 'fedora-%s.json' % self.group_type
            url = self.git_url + filename
            response = requests.get(url, params=params)
            if not bool(response):
                log.warn("Failed to get %r: %r" % (response.url, response))
                continue
            data = response.json()

            # Some of the packages listed *could* be sub-packages, but in the
            # PDC component group we want to deal with parent srpms.  So, use
            # mdapi to convert based on whatevers in the repos right now.
            packages = [
                pdcupdater.utils.subpackage2parent(package, release)
                for package in data['packages']
            ]

            # And return formatted component group data
            yield {
                'group_type': self.group_type,
                'release': release_id,
                'description': 'Deps for %s %s' % (
                    self.group_type,
                    self.git_url,
                ),
                'components': [{
                    'release': release_id,
                    'name': package,
                } for package in packages],
            }

    def handle(self, pdc, msg):
        component_groups = self.atomic_component_groups_from_git(pdc)
        for group in component_groups:
            self._update_atomic_component_group(pdc, group)

    def audit(self, pdc):
        # Query the data sources
        git_groups = list(self.atomic_component_groups_from_git(pdc))
        pdc_groups = [
            group for group in pdc.get_paged(pdc['component-groups']._)
            if group['group_type'] == self.group_type
        ]

        # Invert the lists of dicts into dicts of lists
        invert = lambda collection: dict([(
            group['release'],
            [component['name'] for component in group['components']]
        ) for group in collection ])
        git_groups = invert(git_groups)
        pdc_groups = invert(pdc_groups)

        # Associate the two by release and normalize
        present, absent = {}, {}
        for release in set(git_groups.keys() + pdc_groups.keys()):
            # Convert each group to a set
            left = set(git_groups.get(release, []))
            right = set(pdc_groups.get(release, []))

            # Find and store their difference
            present[release] = right - left
            absent[release] = left - right

            # If the diff is empty, remove the key so we don't trigger an alert
            if not present[release]:
                del present[release]
            if not absent[release]:
                del absent[release]

        return present, absent

    def initialize(self, pdc):
        component_groups = self.atomic_component_groups_from_git(pdc)
        for group in component_groups:
            self._update_atomic_component_group(pdc, group)

    def _update_atomic_component_group(self, pdc, component_group):
        # Make sure our pre-requisites exist
        pdcupdater.utils.ensure_component_group_exists(pdc, component_group)
        for component in component_group['components']:
            pdcupdater.utils.ensure_release_component_exists(
                pdc, component['release'], component['name'])

        # Figure out the primary key for this group we have here..
        group_pk = pdcupdater.utils.get_group_pk(pdc, component_group)

        # And perform the update with a PUT
        pdc['component-groups'][group_pk]._ = component_group
