# !/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


from time import strftime, localtime
from enigma import gPixmapPtr
from Components.config import config
from .Debug import logger
from .ServiceUtils import getPicon
from .ConfigInit import ROWS
from .Index import idx
from .EventUtils import find_time_event_index


class Column:
    """Class handling TV channel display and events formatting."""

    def __init__(self, parent):
        """
        Initialize Column class with reference to parent TVMagazineCockpit instance.

        Args:
            parent: Parent TVMagazineCockpit instance for UI access
        """
        self.parent = parent
        self.navigation = self.parent.navigation

    def showColumn(self, event_list, service_ref, channel):
        """
        Display events for a specific channel in its designated column.

        Args:
            events: List of events for the channel
            service_ref: Service reference identifier for the channel
        """

        i = self.parent.page_channel_list.index(service_ref)
        logger.info("Processing channel column: %s", i)
        # debug("event_list: %s", event_list)

        self.parent.list_columns[i] = event_list

        if self.parent.prime_event_indices[i] == -1:
            prime_event_index = find_time_event_index(
                event_list, self.parent.navigation.getTimestamp("20:15"))
            self.parent.prime_event_indices[i] = prime_event_index
            if prime_event_index != -1:
                self.showPrimeEvent(
                    i, event_list[prime_event_index], service_ref, channel)
            else:
                self.showPrimeEvent(i, {}, service_ref, channel)

        current_event_index = find_time_event_index(
            event_list, self.parent.timestamp)
        self.parent.list_indices[i] = current_event_index
        # Extract a subset of events around the current index
        sub_list = []
        if event_list:
            sub_list = event_list[max(
                0, current_event_index - 1):current_event_index - 1 + ROWS]
        # Pad the list to ensure it has ROWS number of items
        while len(sub_list) < ROWS:
            sub_list.append([" ", " ", " ", " ", 0])

        self.parent["list%s" % i].l.setList(sub_list)
        self.parent["list%s" % i].moveToIndex(
            1)  # Position at the current event

    def showPrimeEvent(self, i, event, service_ref, channel):
        """Display prime time event information and thumbnail."""
        logger.info("Prime event: %s", event)
        if event:
            data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
            channel_id = channel[data_source_id]
            self.parent["channel%s" % i].setText(channel["name"])
            self.parent["time%s" % i].setText(
                strftime("%H:%M", localtime(event[idx["startTime"]])))
            self.parent["description%s" % i].setText(event[idx["title"]])
            self.parent["picon%s" % i].instance.setPixmap(
                getPicon(service_ref))

            detailed_event = self.parent.tvmagazine_data.getDetailedEvent(
                event)
            url = detailed_event[idx["photo_url"]]
            start_time = event[idx["startTime"]]
            if url:
                ident = "%s-%s" % (start_time, channel_id)
                self.parent.showPicture(
                    self.parent["programpix%s" % i], "programpix-", ident, url)
        else:
            self.parent["channel%s" % i].setText("")
            self.parent["time%s" % i].setText("")
            self.parent["description%s" % i].setText("")
            self.parent["picon%s" % i].instance.setPixmap(gPixmapPtr())
            self.parent["list%s" % i].l.setList([])
            self.parent["programpix%s" % i].instance.setPixmap(gPixmapPtr())
