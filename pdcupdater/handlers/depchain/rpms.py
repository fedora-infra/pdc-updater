""" Handlers for an RPM dependency chain model.

The idea here is that these are two of what will eventually be many handlers
that build and maintain a dependency chain in PDC.

There are two handlers here.  They both respond to koji 'tag' events. One of
them figures out what the build required at *build* time, and updates PDC with
that. The other figures out what the build requires at *run* time, and updates
PDC with that.

"""

import logging
import time

import pdcupdater.handlers
import pdcupdater.services
from pdcupdater.utils import (
    tag2release,
    interesting_tags,
)


log = logging.getLogger(__name__)


class BaseRPMDepChainHandler(pdcupdater.handlers.BaseHandler):
    """ Abstract base class. """

    # A list of the types of relationships this thing manages.
    # This needs to be overridden by subclasses of this base class.
    managed_types = None

    def __init__(self, *args, **kwargs):
        super(BaseRPMDepChainHandler, self).__init__(*args, **kwargs)
        self.koji_url = self.config['pdcupdater.koji_url']

    @property
    def topic_suffixes(self):
        return ['buildsys.tag']

    def can_handle(self, msg):
        if not any([msg['topic'].endswith(suffix)
                    for suffix in self.topic_suffixes]):
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

    def _yield_pdc_relationships(self, pdc, release_id):
        for type in self.managed_types:
            entries = pdc.get_paged(
                pdc['release-component-relationships']._,
                from_component_release=release_id,
                type=type,
            )
            for entry in entries:
                yield entry

    def _yield_koji_relationships(self, pdc, tag):

        release_id, release = tag2release(tag)
        # TODO -- this tag <-> release agreement is going to break down with modularity.

        pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

        builds = pdcupdater.services.koji_builds_in_tag(self.koji_url, tag)

        for build in builds:
            parent = {
                'name': build['name'],
                'release': {'release_id': release_id},
            }

            relationships = self.get_koji_relationships_from_build(
                self.koji_url, build['build_id'])
            relationships = list(relationships)

            for relationship, child in relationships:
                child = {'name': child, 'release': {'release_id': release_id}}
                yield parent, relationship, child

    def handle(self, pdc, msg):
        tag = msg['msg']['tag']
        release_id, release = tag2release(tag)

        # TODO -- this tag <-> release agreement is going to break down with modularity.
        pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

        name = msg['msg']['name']
        parent = pdcupdater.utils.ensure_release_component_exists(
            pdc, release_id, name)

        # Go to sleep due to a race condition that is koji's fault.
        # It publishes a fedmsg message before the task is actually done and
        # committed to their database.  In the next step, we try to query
        # them -- but if the task isn't done, we get an exception.
        time.sleep(1)

        # First, go through all of the relationships that we learn from koji,
        # and add them to PDC.  Some may already be present, but we may add new
        # ones here.
        koji_relationships = self.get_koji_relationships_from_build(
            self.koji_url, msg['msg']['build_id'])
        for type, child in koji_relationships:
            child = pdcupdater.utils.ensure_release_component_exists(
                pdc, release_id, child)
            pdcupdater.utils.ensure_release_component_relationship_exists(
                pdc, parent=parent, child=child, type=type)

        # Lastly, go through all of the relationships that we know of now in
        # PDC and find any that do not appear in koji.  These must be old
        # relationships that are no longer relevant.
        pdc_relationships = list(self._yield_pdc_relationships(pdc, release_id))
        for entry in pdc_relationships:
            pdcupdater.utils.delete_release_component_relationship(
                pdc, parent=parent, child=child, type=type)

    def audit(self, pdc):
        present, absent = set(), set()
        tags = interesting_tags()

        for tag in tags:
            log.debug("Starting audit of tag %r." % tag)
            release_id, release = tag2release(tag)

            # Query Koji and PDC to figure out their respective opinions
            koji_relationships = list(self._yield_koji_relationships(pdc, tag))
            pdc_relationships = list(self._yield_pdc_relationships(pdc, release_id))

            # Filter out any irrelevant relationships (those of some type
            # managed by a different pdc updater Handler).
            pdc_relationships = [
                entry for entry in pdc_relationships
                if entry['type'] in self.managed_types
            ]

            # normalize the two lists
            koji_relationships = set(["%s/%s %s %s/%s" % (
                parent['name'],
                parent['release']['release_id'],
                relationship,
                child['name'],
                child['release']['release_id'],
            ) for parent, relationship, child in koji_relationships])
            pdc_relationships = set(["%s/%s %s %s/%s" % (
                entry['from_component']['name'],
                entry['from_component']['release'],
                entry['type'],
                entry['to_component']['name'],
                entry['to_component']['release'],
            ) for entry in pdc_relationships])

            # use set operators to determine the difference
            present = present.union(pdc_relationships - koji_relationships)
            absent = absent.union(koji_relationships - pdc_relationships)

        return present, absent

    def initialize(self, pdc):
        tags = interesting_tags()

        for tag in tags:
            log.debug("Starting audit of tag %r." % tag)
            release_id, release = tag2release(tag)
            pdcupdater.utils.ensure_release_exists(pdc, release_id, release)

            koji_relationships = self._yield_koji_relationships(pdc, tag)
            for parent, type, child in koji_relationships:
                pdcupdater.utils.ensure_release_component_exists(
                    pdc, parent['release']['release_id'], parent['name'])
                pdcupdater.utils.ensure_release_component_exists(
                    pdc, child['release']['release_id'], child['name'])
                pdcupdater.utils.ensure_release_component_relationship_exists(
                    pdc, parent=parent, child=child, type=type)



class NewRPMBuildTimeDepChainHandler(BaseRPMDepChainHandler):
    """ When a build gets tagged, update PDC with buildroot info. """

    # A list of the types of relationships this thing manages.
    managed_types = ('RPMBuildRequires', 'RPMBuildRoot')

    def get_koji_relationships_from_build(self, koji_url, build_id):

        # Get all RPMs for a build..
        build, rpms = pdcupdater.services.koji_rpms_from_build(
            koji_url, build_id)

        # https://pdc.fedoraproject.org/rest_api/v1/rpms/
        for filename in rpms:
            # Look up the *build time* deps
            buildroot = pdcupdater.services.koji_list_buildroot_for(
                self.koji_url, filename)
            for entry in buildroot:
                child = entry['name']

                if entry['is_update']:
                    type = 'RPMBuildRequires'
                else:
                    type = 'RPMBuildRoot'

                yield type, child


class NewRPMRunTimeDepChainHandler(BaseRPMDepChainHandler):
    """ When a build gets tagged, update PDC with rpm dep info. """

    # A list of the types of relationships this thing manages.
    managed_types = ('RPMRequires',)

    def get_koji_relationships_from_build(self, koji_url, build_id):

        # Get all RPMs for a build..
        build, rpms = pdcupdater.services.koji_rpms_from_build(
            koji_url, build_id)

        for filename in rpms:
            # Look up the *install time* deps
            requirements = pdcupdater.services.koji_yield_rpm_requires(
                self.koji_url, filename)
            for name, qualifier, version in requirements:
                # XXX - we're dropping any >= or <= information here, which is
                # OK for now.  All we need to know is that there is a
                # dependency.
                yield 'RPMRequires', name
