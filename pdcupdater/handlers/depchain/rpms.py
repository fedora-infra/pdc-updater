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


class NewRPMBuildTimeDepChainHandler(BaseKojiDepChainHandler):
    """ When a build gets tagged, update PDC with buildroot info. """

    # A list of the types of relationships this thing manages.
    managed_types = ('RPMBuildRequires', 'RPMBuildRoot')
    # The types of the parents and children in our managed relationships
    parent_type = 'rpm'
    child_type = 'rpm'

    def interesting_tags(self):
        return pdcupdater.utils.interesting_tags()

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


class NewRPMRunTimeDepChainHandler(BaseKojiDepChainHandler):
    """ When a build gets tagged, update PDC with rpm dep info. """

    # A list of the types of relationships this thing manages.
    managed_types = ('RPMRequires',)
    # The types of the parents and children in our managed relationships
    parent_type = 'rpm'
    child_type = 'rpm'

    def interesting_tags(self):
        return pdcupdater.utils.interesting_tags()

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
