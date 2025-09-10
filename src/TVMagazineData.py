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


from Components.config import config
from .Debug import logger
from .TVFAData import TVFAData
from .TVMData import TVMData
from .TVSData import TVSData


class TVMagazineData():
    def __init__(self, channel_dict):
        self.channel_dict = channel_dict
        self.data_sources = {
            "tvfa": TVFAData,
            "tvm": TVMData,
            "tvs": TVSData
        }

    def downloadEvents(self, day, page_channel_list, events, callback):
        logger.info("page_channel_id_list: %s, day: %s",
                    page_channel_list, day)
        tv_data_mgr = self.data_sources[config.plugins.tvmagazinecockpit.data_source.value](
            self.channel_dict)
        tv_data_mgr.downloadEvents(day, page_channel_list, events, callback)

    def getDetailedEvent(self, event):
        if config.plugins.tvmagazinecockpit.data_source.value == "tvs":
            tv_data_mgr = self.data_sources[config.plugins.tvmagazinecockpit.data_source.value](
                self.channel_dict)
            event = tv_data_mgr.getDetailedEvent(event)
        return event
