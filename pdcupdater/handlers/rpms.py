import json
import logging

import requests
import dogpile.cache

from pdc_client import get_paged

import pdcupdater.handlers


log = logging.getLogger(__name__)

cache = dogpile.cache.make_region()
cache.configure('dogpile.cache.memory', expiration_time=300)


@cache.cache_on_arguments()
def bodhi_releases():
    # TODO -- get these releases from PDC, instead of from Bodhi
    url = 'https://bodhi.fedoraproject.org/releases'
    response = requests.get(url, params=dict(rows_per_page=100))
    if not bool(response):
        raise IOError('Failed to talk to %r: %r' % (url, response))
    return response.json()['releases']


@cache.cache_on_arguments()
def rawhide_tag():
    # TODO - get this tag from PDC, instead of guessing from pkgdb
    url = 'https://admin.fedoraproject.org/pkgdb/api/collections/'
    response = requests.get(url, params=dict(clt_status="Under Development"))
    if not bool(response):
        raise IOError('Failed to talk to %r: %r' % (url, response))
    collections = response.json()['collections']
    rawhide = [c for c in collections if c['koji_name'] == 'rawhide'][0]
    return 'f' + rawhide['dist_tag'].strip('.fc')


def interesting_tags():
    releases = bodhi_releases()
    stable_tags = [r['stable_tag'] for r in releases]
    return stable_tags + [rawhide_tag()]


class NewRPMHandler(pdcupdater.handlers.BaseHandler):
    """ When a new build is tagged into rawhide or a stable release. """

    def __init__(self, *args, **kwargs):
        super(NewRPMHandler, self).__init__(*args, **kwargs)
        self.koji_url = self.config['pdcupdater.koji_url']

    def can_handle(self, msg):
        if not msg['topic'].endswith('buildsys.tag'):
            return False

        # Ignore secondary arches for now
        if msg['msg']['instance'] != 'primary':
            return False

        interesting = interesting_tags()
        tag = msg['msg']['tag']

        if tag not in interesting:
            log.debug("%r not in %r.  Skipping."  % (tag, interesting))
            return False

        return True

    def handle(self, pdc, msg):
        tag = msg['msg']['tag']
        lookup = {r['stable_tag']: r for r in bodhi_releases()}
        release_id = lookup.get(tag, {'dist_tag': rawhide_tag()})['dist_tag']

        # https://pdc.fedorainfracloud.org/rest_api/v1/rpms/
        data = dict(
            name=msg['msg']['name'],
            version=msg['msg']['version'],
            release=msg['msg']['release'],
            arch='src', # TODO --handle this for real
            epoch=0, # TODO -- handle this
            srpm_name='undefined...', # TODO -- handle this
            linked_releases=[
                release_id,
            ],
        )
        pdc['rpms']._(data)

    def audit(self, pdc):
        # Query the data sources
        koji_rpms = self._gather_koji_rpms(pdc)
        pdc_rpms = get_paged(pdc['rpms']._)

        # Normalize the lists before comparing them.
        koji_rpms = set([json.dumps(r, sort_keys=True) for r in koji_rpms])
        pdc_rpms = set([json.dumps(r, sort_keys=True) for r in pdc_rpms])

        # use set operators to determine the difference
        present = pdc_rpms - koji_rpms
        absent = koji_rpms - pdc_rpms

        return present, absent

    def initialize(self, pdc):
        # Get a list of all rpms in koji
        bulk_payload = self._gather_koji_rpms(pdc)
        # And send it to PDC
        pdc['rpms']._(bulk_payload)

    def _gather_koji_rpms(self, pdc):
        koji_rpms = {
            tag: pdcupdater.services.koji_builds_in_tag(tag, self.koji_url)
            for tag in interesting_tags()
        }

        # Flatten into a list and augment the koji dict with tag info.
        return [
            dict(
                name=rpm['name'],
                version=rpm['version'],
                release=rpm['release'],
                epoch=rpm['epoch'],
                arch=rpm['arch'],
                linked_releases=[tag],
                srpm_name='undefined...', # TODO -- handle this
            )
            for tag, rpms in koji_rpms.items()
            for rpm in rpms
        ]
