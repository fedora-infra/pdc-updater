import json
import logging
import time

import pdcupdater.handlers
import pdcupdater.services
from pdcupdater.utils import (
    tag2release,
    interesting_tags,
)


log = logging.getLogger(__name__)


class NewRPMHandler(pdcupdater.handlers.BaseHandler):
    """ When a new build is tagged into rawhide or a stable release. """

    def __init__(self, *args, **kwargs):
        super(NewRPMHandler, self).__init__(*args, **kwargs)
        self.koji_url = self.config['pdcupdater.koji_url']

    @property
    def topic_suffixes(self):
        return ['buildsys.tag']

    def can_handle(self, pdc, msg):
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

        # Go to sleep due to a race condition that is koji's fault.
        # It publishes a fedmsg message before the task is actually done and
        # committed to their database.  In the next step, we try to query
        # them -- but if the task isn't done, we get an exception.
        time.sleep(1)

        build, rpms = pdcupdater.services.koji_rpms_from_build(
            self.koji_url, msg['msg']['build_id'])

        # https://pdc.fedoraproject.org/rest_api/v1/rpms/
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
        pdc_rpms = pdc.get_paged(pdc['rpms']._)

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
            for entry in batch:
                pdc['rpms']._(entry)

    def _gather_koji_rpms(self):
        koji_rpms = {
            tag: pdcupdater.services.koji_rpms_in_tag(self.koji_url, tag)
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
