import os
import logging
import errno
import re

import beanbag
import pdc_client
import pdcupdater.handlers
import pdcupdater.services

import hashlib

import gi
gi.require_version('Modulemd', '1.0') # noqa
from gi.repository import Modulemd

log = logging.getLogger(__name__)


class ModuleStateChangeHandler(pdcupdater.handlers.BaseHandler):
    """ When the state of a module changes. """

    processing_states = set(('done', 'ready'))
    other_states = set(('wait', 'building'))
    irrelevant_states = set(('init', 'build',))
    relevant_states = processing_states.union(other_states)
    error_states = set(('failed',))
    valid_states = relevant_states.union(error_states).union(irrelevant_states)

    def __init__(self, *args, **kwargs):
        super(ModuleStateChangeHandler, self).__init__(*args, **kwargs)
        self.koji_url = self.config['pdcupdater.koji_url']

    @property
    def topic_suffixes(self):
        return [
            'mbs.module.state.change',
        ]

    def can_handle(self, pdc, msg):
        if not any([msg['topic'].endswith(s) for s in self.topic_suffixes]):
            return False

        state = msg['msg']['state_name']

        if state not in self.valid_states:
            log.error("Invalid module state '{}', skipping.".format(state))
            return False

        if state not in self.relevant_states:
            log.debug("Non-relevant module state '{}', skipping.".format(
                state))
            return False

        return True

    @staticmethod
    def get_pdc_api(pdc):
        """Determine if the new "modules" API is available for use. This API
        supersedes "unreleasedvariants" but provides backwards-compatible
        data for it."""
        try:
            pdc['modules']._(page_size=1)
            return 'modules'
        except beanbag.BeanBagException as error:
            if error.response.status_code == 404:
                return 'unreleasedvariants'
            else:
                raise

    def get_uid(self, body):
        """Returns the proper UID based on the message body and PDC API."""
        name = body['name']
        stream = body['stream']
        version = body['version']
        uid = '{n}:{s}:{v}'.format(n=name, s=stream, v=version)
        if self.pdc_api == 'modules':
            # Check to see if the context was provided. Only MBS v1.6+ will
            # provide this value.
            context = body.get('context', '00000000')
            uid = ':'.join([uid, context])
        return uid

    def get_module_rpms(self, pdc, module):
        """
        Returns the list of rpms in the format of the "rpms" key for the
        "modules" PDC endpoint. The list is obtained from the Koji tag defined
        by the "koji_tag" propery of the input module.
        """
        mmd = Modulemd.Module.new_from_string(module['modulemd'])
        mmd.upgrade()

        koji_rpms = pdcupdater.services.koji_rpms_in_tag(
            self.koji_url, module["koji_tag"])

        rpms = []
        # Flatten into a list and augment the koji dict with tag info.
        for rpm in koji_rpms:
            data = dict(
                name=rpm['name'],
                version=rpm['version'],
                release=rpm['release'],
                epoch=rpm['epoch'] or 0,
                arch=rpm['arch'],
                srpm_name=rpm['srpm_name'],
            )

            if 'srpm_nevra' in rpm and rpm['arch'] != 'src':
                data['srpm_nevra'] = rpm['srpm_nevra']

            # For SRPM packages, include the hash and branch from which is
            # has been built.
            if (rpm['arch'] == 'src'
                    and rpm['name'] in mmd.get_rpm_components().keys()
                    and 'rpms' in mmd.get_xmd()['mbs'].keys()
                    and rpm['name'] in mmd.get_xmd()['mbs']['rpms']):
                mmd_rpm = mmd.get_rpm_components()[rpm['name']]
                xmd_rpm = mmd.get_xmd()['mbs']['rpms'][rpm['name']]
                data["srpm_commit_hash"] = xmd_rpm['ref']
                if xmd_rpm['ref'] != mmd_rpm.get_ref():
                    data["srpm_commit_branch"] = mmd_rpm.get_ref()
            rpms.append(data)

        return rpms

    def handle(self, pdc, msg):
        log.debug("handle(pdc, msg=%r)" % msg)
        body = msg['msg']
        state = body['state_name']

        if state not in self.relevant_states:
            log.warn("Non-relevant module state '{}', skipping.".format(
                state))
            return

        log.debug('Determining which PDC API to use.')
        self.pdc_api = self.get_pdc_api(pdc)
        log.debug('Using the "{0}" PDC API.'.format(self.pdc_api))

        module = self.get_or_create_module(pdc, body)

        if body['state'] == 5:
            if self.pdc_api == 'modules':
                uid = module['uid']
            else:
                uid = module['variant_uid']
            log.info("%r ready.  Patching with rpms and active=True." % uid)
            rpms = self.get_module_rpms(pdc, module)
            pdc[self.pdc_api][uid]._ += {'active': True, 'rpms': rpms}

    def create_module(self, pdc, body):
        """Creates a module in PDC."""
        log.debug("create_module(pdc, body=%r)" % body)

        mmd = Modulemd.Module.new_from_string(body['modulemd'])
        mmd.upgrade()

        runtime_deps = []
        build_deps = []
        for deps in mmd.get_dependencies():
            for dependency, streams in deps.get_requires().items():
                for stream in streams.get():
                    runtime_deps.append(
                        {'dependency': dependency, 'stream': stream})
            for dependency, streams in deps.get_buildrequires().items():
                for stream in streams.get():
                    build_deps.append(
                        {'dependency': dependency, 'stream': stream})

        name = body['name']
        stream = body['stream']
        version = body['version']
        tag_str = '.'.join(self.get_uid(body).split(':'))
        tag_hash = hashlib.sha1(tag_str).hexdigest()[:16]
        koji_tag = 'module-' + tag_hash

        if self.pdc_api == 'modules':
            data = {
                'name': name,
                'stream': stream,
                'version': version,
                # Check if this was provided by MBS
                'context': body.get('context', '00000000')
            }
        else:
            data = {
                'variant_id': name,
                'variant_uid': self.get_uid(body),
                'variant_name': name,
                'variant_version': stream,
                'variant_release': version,
                'variant_type': 'module',
            }

        data['koji_tag'] = koji_tag
        data['runtime_deps'] = runtime_deps
        data['build_deps'] = build_deps
        data['modulemd'] = body['modulemd']
        module = pdc[self.pdc_api]._(data)

        return module

    def get_or_create_module(self, pdc, body):
        """Attempts to retrieve the corresponding module from PDC, or if it's
        missing, creates it."""
        log.debug("get_or_create_module(pdc, body=%r)" % body)

        uid = self.get_uid(body)
        log.info("Looking up module %r" % uid)
        if self.pdc_api == 'modules':
            query = {'uid': uid}
        else:
            query = {'variant_uid': uid}
        modules = pdc[self.pdc_api]._(page_size=-1, **query)

        if not modules:
            log.info("%r not found.  Creating." % uid)  # a new module!
            return self.create_module(pdc, body)
        else:
            return modules[0]

    def audit(self, pdc):
        pass

    def initialize(self, pdc):
        pass
