import os
import logging
import errno
import re
from subprocess import check_call, STDOUT

import beanbag
import pdcupdater.handlers
import pdcupdater.services
from pdcupdater.utils import TmpDir, PushPopD

import modulemd

log = logging.getLogger(__name__)


class ModuleStateChangeHandler(pdcupdater.handlers.BaseHandler):
    """ When the state of a module changes. """

    tree_processing_states = set(('done', 'ready'))
    other_states = set(('init', 'wait', 'building'))
    relevant_states = tree_processing_states.union(other_states)
    error_states = set(('failed',))
    valid_states = relevant_states.union(error_states)

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

    @property
    def topic_suffixes(self):
        return ['rida.module.state.change']

    def can_handle(self, msg):
        if not any([msg['topic'].endswith(s) for s in self.topic_suffixes]):
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
        body = msg['msg']
        state = body['state']

        if state not in self.relevant_states:
            log.warn("Non-relevant module state '{}', skipping.".format(
                state))
            return

        unreleased_variant = self.get_or_create_unreleased_variant(pdc, body)

        # trees are only present when a module is done building, i.e. states
        # 'done' or 'ready'
        if 'topdir' in body:
            self.handle_new_tree(pdc, body, unreleased_variant)

    def get_mmd_from_scm(self, scmurl):
        with TmpDir(prefix="pdcupdater-") as tmpdir, PushPopD(tmpdir), \
                open(os.devnull, "w") as devnull:
            m = self.scmurl_re.match(scmurl)
            if not m:
                raise RuntimeError("Can't parse SCM URL: {}".format(scmurl))
            giturl = m.group('giturl')
            repopath = m.group('repopath').rstrip("/")
            modpath = m.group('modpath')
            revision = m.group('revision')
            modname = repopath.rsplit("/", 1)[1]
            if modname.endswith(".git"):
                modname = modname[:-4]

            log.debug("Cloning {}".format(giturl))
            check_call(["git", "clone", "-n", giturl, modname],
                       stdout=devnull, stderr=STDOUT)
            os.chdir(modname)

            log.debug("Checking out revision {}".format(revision))
            check_call(["git", "reset", "--hard", revision],
                       stdout=devnull, stderr=STDOUT)

            mmd_yaml = modname + ".yaml"
            if modpath:
                mmd_yaml = "/".join((modpath, mmd_yaml))
            log.debug("Reading/parsing {}".format(mmd_yaml))
            mmd = modulemd.ModuleMetadata()
            mmd.load(mmd_yaml)

            return mmd

    def create_unreleased_variant(self, pdc, body):
        """Creates an UnreleasedVariant for a module in PDC. Checks out the
        module metadata from the supplied SCM repository (currently only
        anonymous GIT is supported)."""

        scmurl = body['scmurl']
        mmd = self.get_mmd_from_scm(scmurl)

        runtime_deps = []
        for dep, ver in mmd.requires.items():
            if ver is not None:
                runtime_deps.append("{} >= {}".format(dep, ver))
            else:
                runtime_deps.append(dep)

        build_deps = []
        for dep, ver in mmd.buildrequires.items():
            if ver is not None:
                build_deps.append("{} >= {}".format(dep, ver))
            else:
                build_deps.append(dep)

        name = body['name']
        version = body['version']
        release = body['release']
        variant_uid = "{n}-{v}-{r}".format(n=name, v=version, r=release)
        variant_id = variant_uid.lower()
        koji_tag = "module-" + variant_id

        unreleased_variant = pdc['unreleasedvariants']._({
            'variant_id': variant_id,
            'variant_uid': variant_uid,
            'variant_name': name,
            'variant_version': version,
            'variant_release': release,
            'variant_type': 'module',
            'koji_tag': koji_tag,
            'runtime_deps': runtime_deps,
            'build_deps': build_deps,
        })

        return unreleased_variant

    def get_or_create_unreleased_variant(self, pdc, body):
        """We get multiple messages for each module n-v-r. Attempts to retrieve
        the corresponding UnreleasedVariant from PDC, or if it's missing,
        creates it."""

        variant_uid = "{name}-{version}-{release}".format(**body)
        variant_id = variant_uid.lower()

        try:
            unreleased_variant = pdc['unreleasedvariants'][variant_id]._()
        except beanbag.BeanBagException as e:
            if e.response.status_code != 404:
                raise
            # a new module!
            unreleased_variant = self.create_unreleased_variant(pdc, body)
        return unreleased_variant

    def handle_new_tree(self, pdc, body, unreleased_variant):
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
