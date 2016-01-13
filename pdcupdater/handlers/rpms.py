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


def tag2release(tag):
    if tag == rawhide_tag():
        release = {
            'name': 'Fedora',
            'short': 'fedora',
            'version': tag.strip('f'),
            'release_type': 'ga',
        }
        release_id = "{short}-{version}-fedora-NEXT".format(**release)
    else:
        bodhi_info = {r['stable_tag']: r for r in bodhi_releases()}[tag]
        if 'EPEL' in bodhi_info['id_prefix']:
            release = {
                'name': 'Fedora EPEL',
                'short': 'epel',
                'version': bodhi_info['version'],
                'release_type': 'updates',
            }
        else:
            release = {
                'name': 'Fedora Updates',
                'short': 'fedora',
                'version': bodhi_info['version'],
                'release_type': 'updates',
            }
        release_id = "{short}-{version}-fedora-NEXT-{release_type}".format(**release)

    return release_id, release


class NewRPMHandler(pdcupdater.handlers.BaseHandler):
    """ When a new build is tagged into rawhide or a stable release. """

    def __init__(self, *args, **kwargs):
        super(NewRPMHandler, self).__init__(*args, **kwargs)
        self.koji_url = self.config['pdcupdater.koji_url']

    @property
    def topic_suffixes(self):
        return ['buildsys.tag']

    def can_handle(self, msg):
        if not msg['topic'].endswith('buildsys.tag'):
            return False

        # Ignore secondary arches for now
        if msg['msg']['instance'] != 'primary':
            log.debug("From %r.  Skipping." % (msg['msg']['instance']))
            return False

        interesting = interesting_tags()
        tag = msg['msg']['tag']

        if tag not in interesting:
            log.debug("%r not in %r.  Skipping."  % (tag, interesting))
            return False

        return True

    def handle(self, pdc, msg):
        tag = msg['msg']['tag']
        release_id, release = tag2release(tag)
        pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

        build, rpms = pdcupdater.services.koji_rpms_from_build(
            self.koji_url, msg['msg']['build_id'])

        # https://pdc.fedorainfracloud.org/rest_api/v1/rpms/
        for rpm in rpms:
            # Start with podofo-0.9.1-17.el7.ppc64.rpm
            name, version, release = rpm.rsplit('-', 2)
            release, arch, _ = release.rsplit('.', 2)
            data = dict(
                name=name,
                version=version,
                release=release,
                arch=arch,
                epoch=build['epoch'] or 0,
                srpm_name=build['name'],
                srpm_nevra=None,  # This gets overwritten below
                linked_releases=[
                    release_id,
                ],
            )
            if arch != 'src':
                data['srpm_nevra'] = build['nvr']
            log.info("Adding rpm %s to PDC release %s" % (rpm, release_id))
            pdc['rpms']._(data)

    def audit(self, pdc):
        # Query the data sources
        koji_rpms = sum(self._gather_koji_rpms(), [])
        pdc_rpms = get_paged(pdc['rpms']._)

        # Normalize the lists before comparing them.
        koji_rpms = set([json.dumps(r, sort_keys=True) for r in koji_rpms])
        pdc_rpms = set([json.dumps(r, sort_keys=True) for r in pdc_rpms])

        # use set operators to determine the difference
        present = pdc_rpms - koji_rpms
        absent = koji_rpms - pdc_rpms

        return present, absent

    def initialize(self, pdc):
        # Get a list of all rpms in koji and send it to PDC
        for batch in self._gather_koji_rpms():
            log.info("Uploading info about %i rpms to PDC." % len(batch))
            pdc['rpms']._(batch)

    def _gather_koji_rpms(self):
        koji_rpms = {
            tag: pdcupdater.services.koji_builds_in_tag(self.koji_url, tag)
            for tag in interesting_tags()
        }

        # Flatten into a list and augment the koji dict with tag info.
        for tag, rpms in koji_rpms.items():
            yield [
                dict(
                    name=rpm['name'],
                    version=rpm['version'],
                    release=rpm['release'],
                    epoch=rpm['epoch'] or 0,
                    arch=rpm['arch'],
                    linked_releases=[
                        tag2release(tag)[0],  # Just the release_id
                    ],
                    srpm_name=rpm['srpm_name'],
                    srpm_nevra=rpm['arch'] != 'src' and rpm.get('srpm_nevra') or None,
                )
                for rpm in rpms
            ]
