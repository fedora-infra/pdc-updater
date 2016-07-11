import os
import logging
import errno
import re

import beanbag
import pdcupdater.handlers
import pdcupdater.services

log = logging.getLogger(__name__)


class NewTreeHandler(pdcupdater.handlers.BaseHandler):
    """ When a new tree is created """

    relevant_states = ('done', 'ready')
    valid_states = relevant_states + ('init', 'wait', 'building', 'failed')

    tree_id_re = re.compile(
        r"(?P<name>[^-]+)-(?P<version>[^-]+)-"
        r"(?P<date>[0-9]{8})\.(?P<spin>[0-9]+)")

    rpm_fname_re = re.compile(
        r"(?P<name>.+)-"
        r"(?:(?P<epoch>[^:]+):)?(?P<version>[^-:]+)-(?P<release>[^-]+)."
        r"(?P<arch>[^\.]+).rpm")

    @property
    def topic_suffixes(self):
        return ['module.state.change']

    def can_handle(self, msg):
        if not msg['topic'].endswith('module.state.change'):
            return False

        state = msg['msg']['state']

        if state not in self.valid_states:
            log.error("Invalid module state '{}', skipping.".format(state))
            return False

        if state not in self.relevant_states:
            log.debug("Non-relevant module state '{}', skipping.".format(
                state))
            return False

        return True

    def handle(self, pdc, msg):
        state = msg['msg']['state']

        if state not in self.relevant_states:
            log.warn("Non-relevant module state '{}', skipping.".format(
                state))
            return

        koji_tag = msg['msg']['koji_tag']
        variant_uid = variant_name = msg['msg']['module_uid']
        variant_id = variant_uid.lower()
        variant_version = msg['msg']['module_version']
        topdir = msg['msg']['topdir']
        tree_id = os.path.basename(topdir)

        m = self.tree_id_re.match(tree_id)
        if not m:
            log.error("Unexpected tree id: '{}'".format(tree_id))
            return

        tree_date = m.group('date')
        tree_date = (
            tree_date[0:4] + "-" + tree_date[4:6] + "-" + tree_date[6:8])

        try:
            unreleased_variant = pdc['unreleasedvariants'][variant_id]._()
        except beanbag.BeanBagException as e:
            if e.response.status_code != 404:
                raise
            unreleased_variant = pdc['unreleasedvariants']._({
                'variant_id': variant_id,
                'variant_uid': variant_uid,
                'variant_name': variant_name,
                'variant_version': variant_version,
                'variant_type': 'module',
                'koji_tag': koji_tag,
            })

        # avoid adding trees twice
        try:
            pdc['trees'][tree_id]._()
        except beanbag.BeanBagException as e:
            if e.response.status_code != 404:
                raise
        else:
            log.info("Tree exists already, skipping: {}".format(tree_id))
            return

        arches = [x['name'] for x in pdc['arches']._(page_size=-1)]

        for arch in arches:
            archdir = os.path.join(topdir, arch)
            tree_dict = {
                'arch': arch,
                'variant': unreleased_variant,
                'content_format': ['rpm'],
                'content': {'rpms': {}},
                'url': archdir,
                'tree_id': tree_id,
                'tree_date': tree_date,
            }

            content_dict = tree_dict['content']['rpms']

            # just grab RPMs from base dir, TODO: retrieve from repodata?
            try:
                fnames = os.listdir(archdir)
            except OSError as e:
                if e.errno == errno.ENOENT:
                    log.debug("Skipping non-existent arch {}".format(arch))
                    continue
                raise

            for fname in sorted(fnames):
                m = self.rpm_fname_re.match(fname)
                if not m:
                    log.debug("Skipping over non-RPM file {}".format(fname))
                    continue

                fname_wo_rpm = fname[:-4]

                rpminfo = m.groupdict()

                # TODO: debug RPM category
                if rpminfo['arch'] == 'src':
                    category = 'source'
                else:
                    category = 'binary'

                # TODO: extract RPM signature key?
                sigkey = None

                fpath = os.path.join(archdir, fname)

                content_dict[fname_wo_rpm] = {
                    'category': category,
                    'path': fpath,
                    'sigkey': sigkey
                }

            pdc['trees']._(tree_dict)

    def audit(self, pdc):
        # TODO: find out what trees exist in koji

        # # Query the data sources
        # koji_trees = sum(self._gather_koji_rpms(), [])
        # pdc_trees = pdc.get_paged(pdc['trees']._)

        # # Normalize the lists before comparing them.
        # koji_rpms = set([json.dumps(r, sort_keys=True) for r in koji_rpms])
        # pdc_rpms = set([json.dumps(r, sort_keys=True) for r in pdc_rpms])

        # # use set operators to determine the difference
        # present = pdc_rpms - koji_rpms
        # absent = koji_rpms - pdc_rpms

        # return present, absent

        pass

    def initialize(self, pdc):

        ## Get a list of all rpms in koji and send it to PDC
        #for batch in self._gather_koji_rpms():
        #    log.info("Uploading info about %i rpms to PDC." % len(batch))
        #    for entry in batch:
        #        pdc['rpms']._(entry)

        pass
