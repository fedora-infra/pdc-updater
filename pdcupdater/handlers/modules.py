import os
import logging
import errno
import re

import beanbag
import pdcupdater.handlers
import pdcupdater.services

import modulemd
import hashlib

log = logging.getLogger(__name__)


class ModuleStateChangeHandler(pdcupdater.handlers.BaseHandler):
    """ When the state of a module changes. """

    tree_processing_states = set(('done', 'ready'))
    other_states = set(('wait', 'building'))
    irrelevant_states = set(('init', 'build',))
    relevant_states = tree_processing_states.union(other_states)
    error_states = set(('failed',))
    valid_states = relevant_states.union(error_states).union(irrelevant_states)

    tree_id_re = re.compile(
        r"(?P<name>[^-]+)-(?P<version>[^-]+)-"
        r"(?P<date>[0-9]{8})\.(?P<spin>[0-9]+)")

    rpm_fname_re = re.compile(
        r"(?P<name>.+)-"
        r"(?:(?P<epoch>[^:]+):)?(?P<version>[^-:]+)-(?P<release>[^-]+)."
        r"(?P<arch>[^\.]+).rpm")

    scmurl_re = re.compile(
        r"(?P<giturl>(?:(?P<scheme>git)://(?P<host>[^/]+))?"
        r"(?P<repopath>/[^\?]+))\?(?P<modpath>[^#]*)#(?P<revision>.+)")

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

    def get_unreleased_variant_rpms(self, pdc, variant):
        """
        Returns the list of rpms as defined "rpms" key in "unreleasedvariants"
        PDC endpoint. The list is obtained from the Koji tag defined by
        "koji_tag" value of input variant `variant`.
        """
        mmd = modulemd.ModuleMetadata()
        mmd.loads(variant['modulemd'])

        koji_rpms = pdcupdater.services.koji_rpms_in_tag(
            self.koji_url, variant["koji_tag"])

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
            if (rpm['arch'] == 'src' and rpm['name'] in mmd.components.rpms
                    and 'rpms' in mmd.xmd['mbs']
                    and rpm['name'] in mmd.xmd['mbs']['rpms']):
                mmd_rpm = mmd.components.rpms[rpm['name']]
                xmd_rpm = mmd.xmd['mbs']['rpms'][rpm['name']]
                data["srpm_commit_hash"] = xmd_rpm['ref']
                if xmd_rpm['ref'] != mmd_rpm.ref:
                    data["srpm_commit_branch"] = mmd_rpm.ref
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

        unreleased_variant = self.get_or_create_unreleased_variant(pdc, body)

        if body['state'] == 5:
            uid = unreleased_variant['variant_uid']
            rpms = self.get_unreleased_variant_rpms(pdc, unreleased_variant)
            # This submits an HTTP PATCH.
            # The '/' is necessary to avoid losing the body in a 301.
            pdc['unreleasedvariants'][uid + '/'] += {'variant_uid': uid,
                                                     'active': True,
                                                     'rpms': rpms}

        # trees are only present when a module is done building, i.e. states
        # 'done' or 'ready'
        if 'topdir' in body:
            self.handle_new_tree(pdc, body, unreleased_variant)

    def create_unreleased_variant(self, pdc, body):
        """Creates an UnreleasedVariant for a module in PDC. Checks out the
        module metadata from the supplied SCM repository (currently only
        anonymous GIT is supported)."""
        log.debug("create_unreleased_variant(pdc, body=%r)" % body)

        mmd = modulemd.ModuleMetadata()
        mmd.loads(body['modulemd'])

        runtime_deps = [{'dependency': dependency, 'stream': stream}
                        for dependency, stream in mmd.requires.items()]
        build_deps = [{'dependency': dependency, 'stream': stream}
                      for dependency, stream in mmd.buildrequires.items()]

        name = body['name']
        # TODO: PDC has to be patched to support stream/version instead of
        # version/release, but for now we just do the right mapping here...
        version = body['stream']
        release = body['version']
        variant_uid = "{n}-{v}-{r}".format(n=name, v=version, r=release)
        variant_id = name

        tag_str = '.'.join([name, version, str(release)])
        tag_hash = hashlib.sha1(tag_str).hexdigest()[:16]
        koji_tag = "module-" + tag_hash

        data = {
            'variant_id': variant_id,
            'variant_uid': variant_uid,
            'variant_name': name,
            'variant_version': version,
            'variant_release': release,
            'variant_type': 'module',
            'koji_tag': koji_tag,
            'runtime_deps': runtime_deps,
            'build_deps': build_deps,
            'modulemd': body["modulemd"],
        }
        unreleased_variant = pdc['unreleasedvariants']._(data)

        return unreleased_variant

    def get_or_create_unreleased_variant(self, pdc, body):
        """We get multiple messages for each module n-v-r. Attempts to retrieve
        the corresponding UnreleasedVariant from PDC, or if it's missing,
        creates it."""
        log.debug("get_or_create_unreleased_variant(pdc, body=%r)" % body)

        variant_id =  body['name'] # This is supposed to be equal to name
        # TODO: PDC has to be patched to support stream/version instead of
        # version/release, but for now we just do the right mapping here...
        variant_version =  body['stream'] # This is supposed to be equal to version
        variant_release =  body['version'] # This is supposed to be equal to release
        variant_uid = "%s-%s-%s" % (variant_id, variant_version, variant_release)

        unreleased_variants = pdc['unreleasedvariants']._(
            page_size=-1, variant_uid=variant_uid)
        if not unreleased_variants:
            # a new module!
            unreleased_variant = self.create_unreleased_variant(pdc, body)
        else:
            unreleased_variant = unreleased_variants[0]
        return unreleased_variant

    def handle_new_tree(self, pdc, body, unreleased_variant):
        log.debug("handle_new_tree(pdc, body, unreleased_variant=%r)" % unreleased_variant)
        topdir = body['topdir']
        tree_id = os.path.basename(topdir)

        log.debug("Trying to import tree from topdir '{}'".format(topdir))

        m = self.tree_id_re.match(tree_id)
        if not m:
            log.error("Unexpected tree id: '{}'".format(tree_id))
            return

        tree_date = m.group('date')
        tree_date = (
            tree_date[0:4] + "-" + tree_date[4:6] + "-" + tree_date[6:8])

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
