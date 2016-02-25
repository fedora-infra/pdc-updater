import copy
import logging
import requests

import pdcupdater.handlers
import pdcupdater.services
import pdcupdater.utils

from pdc_client import get_paged


log = logging.getLogger(__name__)
session = requests.Session()

# These are the states of a pungi4 compose that we care about.
# There are other states that we don't care about.. like DOOMED, etc..
final = [
    'FINISHED',
    'FINISHED_INCOMPLETE',
]


class NewComposeHandler(pdcupdater.handlers.BaseHandler):
    """ When pungi-koji finishes a new compose. """

    def __init__(self, *args, **kwargs):
        super(NewComposeHandler, self).__init__(*args, **kwargs)
        self.old_composes_url = self.config['pdcupdater.old_composes_url']

    @property
    def topic_suffixes(self):
        return [
            'pungi.compose.status.change',
        ]

    def can_handle(self, msg):
        if not msg['topic'].endswith('pungi.compose.status.change'):
            return False
        if not msg['msg']['status'] in final:
            return False
        return True

    def handle(self, pdc, msg):
        # This is something like Fedora-24-20151130.n.2 or Fedora-Rawhide-201..
        compose_id = msg['msg']['compose_id']

        # The URL given looks like
        # http://kojipkgs.fedoraproject.org/compose/rawhide/COMPOSEID/compose
        # but we want
        # http://kojipkgs.fedoraproject.org/compose/rawhide/COMPOSEID
        # So handle it carefully, like this
        compose_url = msg['msg']['location']\
            .strip('/')\
            .strip('compose')\
            .strip('/')

        self._import_compose(pdc, compose_id, compose_url)

    def audit(self, pdc):
        # Query the data sources
        old_composes = pdcupdater.services.old_composes(self.old_composes_url)
        pdc_composes = get_paged(pdc['composes']._)

        # normalize the two lists
        old_composes = set([idx for branch, idx, url in old_composes])
        pdc_composes = set([c['compose_id'] for c in pdc_composes])

        # use set operators to determine the difference
        present = pdc_composes - old_composes
        absent = old_composes - pdc_composes

        return present, absent

    def initialize(self, pdc):
        old_composes = pdcupdater.services.old_composes(self.old_composes_url)
        for _, compose_id, url in old_composes:
            try:
                self._import_compose(pdc, compose_id, url)
            except Exception as e:
                if hasattr(e, 'response'):
                    log.exception("Failed to import %r %r" % (url, e.response.text))
                else:
                    log.exception("Failed to import %r %r" % url)


    def _import_compose(self, pdc, compose_id, compose_url):
        base = compose_url + "/compose/metadata"

        url = base + '/composeinfo.json'
        response = session.get(url)
        if not bool(response):
            raise IOError("Failed to get %r: %r" % (url, response))
        composeinfo = response.json()

        # Before we waste any more time pulling down 100MB files from koji and
        # POSTing them back to PDC, let's check to see if we already know about
        # this compose.
        compose_id = composeinfo['payload']['compose']['id']
        log.info("Importing compose %r" % compose_id)
        if pdcupdater.utils.compose_exists(pdc, compose_id):
            log.warn("%r already exists in PDC." % compose_id)
            return

        # OK, go ahead and pull down these gigantic files.
        url = base + '/images.json'
        response = session.get(url)
        if not bool(response):
            raise IOError("Failed to get %r: %r" % (url, response))
        images = response.json()

        url = base + '/rpms.json'
        response = session.get(url)
        if not bool(response):
            raise IOError("Failed to get %r: %r" % (url, response))
        rpms = response.json()

        # PDC demands lowercase
        composeinfo['payload']['release']['short'] = \
            composeinfo['payload']['release']['short'].lower()
        release = copy.copy(composeinfo['payload']['release'])
        release['release_type'] = 'ga'
        release_id = "{short}-{version}".format(**release)
        pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

        # https://github.com/product-definition-center/product-definition-center/issues/228
        # https://pdc.fedoraproject.org/rest_api/v1/compose-images/
        pdc['compose-images']._(dict(
            release_id=release_id,
            composeinfo=composeinfo,
            image_manifest=images,
        ))
        # https://pdc.fedoraproject.org/rest_api/v1/compose-rpms/
        pdc['compose-rpms']._(dict(
            release_id=release_id,
            composeinfo=composeinfo,
            rpm_manifest=rpms,
        ))
