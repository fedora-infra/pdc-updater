import os
import logging
import errno
import re

import beanbag
import pdcupdater.handlers
import pdcupdater.services
import rida


log = logging.getLogger("pdcupdater")
md_ns = {
    'common': "http://linux.duke.edu/metadata/common",
    'repo': "http://linux.duke.edu/metadata/repo",
    'rpm': "http://linux.duke.edu/metadata/rpm"
}


def get_koji_tag(variant_info):
    return "%s-%s-%s" % (variant_info['variant_id'], variant_info['variant_version'], variant_info['variant_release'])

class NewUnreleasedVariantHandler(pdcupdater.handlers.BaseHandler):
    """ When a new tree is created """

    relevant_states = [rida.BUILD_STATES['init']]
    valid_states = relevant_states + [rida.BUILD_STATES[s] for s in ('wait', 'failed', 'done', 'ready')]

    @property
    def topic_suffixes(self):
        return ['rida.module.state.change']

    def can_handle(self, msg):
        print(msg)
        if not msg['topic'].endswith('rida.module.state.change'):
            log.debug("ignoring msg %s" % msg)
            return False
        log.debug("getting state from msg %s" % msg)
        state = int(msg['msg']['state'])

        if state not in self.valid_states:
            log.warn("Invalid module state '{}', skipping.".format(state))
            return False

        if state not in self.relevant_states:
            log.debug("Non-relevant module state '{}', skipping.".format(
                state))
            return False

        return True

    def handle(self, pdc, msg):
        state = msg['msg']['state']
        log.info("handling message")
        variant_info = {
            'variant_id': msg['msg']['name'],
            'variant_uid': msg['msg']['name'],
            'variant_name': msg['msg']['name'],
            'variant_version':msg['msg']['version'],
            'variant_release': msg['msg']['release'],
            'variant_type': 'module',
        }
        variant_info['koji_tag'] = get_koji_tag(variant_info)
        try:
            unreleased_variant = pdc['unreleasedvariants'][variant_info['variant_id']]._()
        except beanbag.BeanBagException as e:
            if e.response.status_code != 404:
                raise
            unreleased_variant = pdc['unreleasedvariants']._(variant_info)

    def audit(self, pdc):
        pass

    def initialize(self, pdc):
        pass
