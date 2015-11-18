# -*- coding: utf-8 -*-
# This file is part of pdc-updater.
#
# pdc-updater is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# pdc-updater is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pdc-updater.  If not, see <http://www.gnu.org/licenses/>.
""" Fedmsg consumer that updates PDC.

Authors:    Ralph Bean <rbean@redhat.com>

"""

import fedmsg.consumers

import pdcupdater.pdc
import pdcupdater.handlers


class PDCUpdater(fedmsg.consumers.FedmsgConsumer):
    topic = '*'
    config_key = 'pdcupdater.enabled'

    def __init__(self, hub):
        super(PDCUpdater, self).__init__(hub)

        if not self._initialized:
            return

        config = self.hub.config

        # Ensure this is present, it should be a dict with a url and creds
        self.pdc_config = config['pdcupdater.pdc']

        # Load all our worker bits.
        self.handlers = list(pdcupdater.handlers.load_handlers(config))

    def consume(self, msg):
        topic, msg = msg['topic'], msg['body']
        idx = msg.get('msg_id', None)
        self.log.debug("Received %r" % idx)

        pdc = pdcupdater.pdc.PDC(self.pdc_config)
        for handler in self.handlers:
            if handler.can_handle(msg):
                self.log.info("%r handling %r %r" % (handler, topic, idx))
                handler.handle(pdc, msg)
