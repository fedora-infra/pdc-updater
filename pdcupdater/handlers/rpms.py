import logging

import requests
import dogpile.cache

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
    # TODO - get this tag from bodhi, instead of guessing from pkgdb
    url = 'https://admin.fedoraproject.org/pkgdb/api/collections/'
    response = requests.get(url, params=dict(clt_status="Under Development"))
    if not bool(response):
        raise IOError('Failed to talk to %r: %r' % (url, response))
    collections = response.json()['collections']
    rawhide = [c for c in collections if c['koji_name'] == 'rawhide'][0]
    return 'f' + rawhide['dist_tag'].strip('.fc')


class NewRPMHandler(pdcupdater.handlers.BaseHandler):
    """ When a new build is tagged into rawhide or a stable release. """

    def can_handle(self, msg):
        if not msg['topic'].endswith('buildsys.tag'):
            return False

        # Ignore secondary arches for now
        if msg['msg']['instance'] != 'primary':
            return False

        releases = bodhi_releases()
        stable_tags = [r['stable_tag'] for r in releases]
        interesting = stable_tags + [rawhide_tag()]

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

    def audit(self):
        raise NotImplementedError()

    def initialize(self):
        raise NotImplementedError()
