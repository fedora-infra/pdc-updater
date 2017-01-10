""" Handlers for an RPM dependency chain model.

The idea here is that these are two of what will eventually be many handlers
that build and maintain a dependency chain in PDC.

There are two handlers here.  They both respond to koji 'tag' events. One of
them figures out what the build required at *build* time, and updates PDC with
that. The other figures out what the build requires at *run* time, and updates
PDC with that.

"""

import collections
import logging
import multiprocessing.pool

import pdcupdater.handlers
import pdcupdater.services
import pdcupdater.utils

from pdcupdater.handlers.depchain.base import BaseKojiDepChainHandler


log = logging.getLogger(__name__)


class BaseRPMDepChainHandler(BaseKojiDepChainHandler):
    """ Intermediary base class providing common methods to rpm handlers. """

    def _yield_koji_relationships_from_tag(self, pdc, tag):

        if self.pdc_tag_mapping:
            release_id, release = pdcupdater.utils.tag2release(tag, pdc=pdc)
        else:
            release_id, release = pdcupdater.utils.tag2release(tag)
        # TODO -- this tag <-> release agreement is going to break down with modularity.

        pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

        rpms = pdcupdater.services.koji_rpms_in_tag(self.koji_url, tag)

        working_build_id = None
        working_set = []
        for i, rpm in enumerate(rpms):
            if not working_build_id:
                working_build_id = rpm['build_id']

            if working_build_id == rpm['build_id']:
                working_set.append(rpm)
                if i != len(rpms) - 1:
                    continue

            def _format_rpm_filename(rpm):
                # XXX - do we need to handle epoch here?  I don't think so.
                return "{name}-{version}-{release}.{arch}.rpm".format(**rpm)

            working_set = [_format_rpm_filename(rpm) for rpm in working_set]
            log.info("Considering build idx=%r, (%i of %i) with %r" % (
                working_build_id, i, len(rpms), working_set))

            relationships = list(self._yield_koji_relationships_from_build(
                self.koji_url, working_build_id, rpms=working_set))

            # Reset our loop variables.
            working_set = []
            working_build_id = rpm['build_id']

            for parent_name, relationship_type, child_name in relationships:
                parent = {
                    'name': parent_name,
                    'release': release_id,
                    #'global_component': build['srpm_name'],  # ideally.
                }
                child = {
                    'name': child_name,
                    'release': release_id,
                }
                yield parent, relationship_type, child

class NewRPMBuildTimeDepChainHandler(BaseRPMDepChainHandler):
    """ When a build gets tagged, update PDC with buildroot info. """

    # A list of the types of relationships this thing manages.
    managed_types = ('RPMBuildRequires', 'RPMBuildRoot')
    # The types of the parents and children in our managed relationships
    parent_type = 'rpm'
    child_type = 'rpm'

    def interesting_tags(self, pdc):
        key = "pdcupdater.%s.interesting_tags" % type(self).__name__

        if not self.config.get(key):
            log.debug("config key %s has no value.  performing queries." % key)
            if self.pdc_tag_mapping:
                return pdcupdater.utils.all_tags_from_pdc(pdc)
            else:
                return pdcupdater.utils.interesting_tags()

        log.debug("using value from config key %s" % key)
        return self.config[key]

    def _yield_koji_relationships_from_build(self, koji_url, build_id, rpms=None):

        # Get all RPMs for a build... only if they're not supplied.
        if not rpms:
            build, rpms = pdcupdater.services.koji_rpms_from_build(
                koji_url, build_id)

        # https://pdc.fedoraproject.org/rest_api/v1/rpms/
        results = collections.defaultdict(set)

        def _get_buildroot(filename):
            log.debug("Looking up buildtime deps in koji for %r" % filename)
            return filename, pdcupdater.services.koji_list_buildroot_for(
                self.koji_url, filename)

        # Look up the *build time* deps, in parallel.  Lots of I/O wait..
        pool = multiprocessing.pool.ThreadPool(self.io_threads)
        buildroots = pool.map(_get_buildroot, rpms)
        pool.close()

        for filename, buildroot in buildroots:
            parent = filename.rsplit('-', 2)[0]

            for entry in buildroot:
                child = entry['name']

                if entry['is_update']:
                    relationship_type = 'RPMBuildRequires'
                else:
                    relationship_type = 'RPMBuildRoot'

                results[parent].add((relationship_type, child,))

        for parent in results:
            for relationship_type, child in results[parent]:
                yield parent, relationship_type, child


class NewRPMRunTimeDepChainHandler(BaseRPMDepChainHandler):
    """ When a build gets tagged, update PDC with rpm dep info. """

    # A list of the types of relationships this thing manages.
    managed_types = ('RPMRequires',)
    # The types of the parents and children in our managed relationships
    parent_type = 'rpm'
    child_type = 'rpm'

    def interesting_tags(self, pdc):
        key = "pdcupdater.%s.interesting_tags" % type(self).__name__

        if not self.config.get(key):
            log.debug("config key %s has no value.  performing queries." % key)
            if self.pdc_tag_mapping:
                return pdcupdater.utils.all_tags_from_pdc(pdc)
            else:
                return pdcupdater.utils.interesting_tags()

        log.debug("using value from config key %s" % key)
        return self.config[key]

    def _yield_koji_relationships_from_build(self, koji_url, build_id, rpms=None):

        # Get all RPMs for a build... only if they're not supplied.
        if not rpms:
            build, rpms = pdcupdater.services.koji_rpms_from_build(
                koji_url, build_id)

        results = collections.defaultdict(set)

        def _get_requirements(filename):
            log.debug("Looking up installtime deps in koji for %r" % filename)
            return filename, pdcupdater.services.koji_yield_rpm_requires(
                self.koji_url, filename)

        # Look up the *build time* deps, in parallel.  Lots of I/O wait..
        # Look up the *install time* deps, in parallel.  Lots of I/O wait..
        pool = multiprocessing.pool.ThreadPool(self.io_threads)
        requirements = pool.map(_get_requirements, rpms)
        pool.close()

        for filename, requirements in requirements:
            parent = filename.rsplit('-', 2)[0]

            for name, qualifier, version in requirements:
                # XXX - we're dropping any >= or <= information here, which is
                # OK for now.  All we need to know is that there is a
                # dependency.
                results[parent].add(('RPMRequires', name,))

        for parent in results:
            for relationship_type, child in results[parent]:
                yield parent, relationship_type, child
