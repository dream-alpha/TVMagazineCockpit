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


import os
from time import time, strftime, localtime
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.config import config
from .EventDetails import EventDetails
from .More import More
from .Menu import Menu
from .__init__ import _
from .EventList import EventList
from .Debug import logger
from .TVMagazineData import TVMagazineData
from .FileUtils import createDirectory
from .ChannelUtils import readChannelList, readChannelDict, getCurrentBouquetName
from .Picture import Picture
from .Column import Column
from .Navigation import Navigation
from .ConfigInit import COLS
from .Page import Page
from .ConfigInit import data_sources
from .CacheUtils import loadEvents


class TVMagazineCockpit(Screen, More, Menu, Picture):
    def __init__(self, session):
        logger.info("...")
        Screen.__init__(self, session)
        self.skinName = "ProgramColumns"
        More.__init__(self, session)
        Menu.__init__(self, session)
        self.channel_dict = readChannelDict()
        self.channel_list = readChannelList(self.channel_dict)
        self.tvmagazine_data = TVMagazineData(self.channel_dict)
        self.date_str = strftime("%Y-%m-%d", localtime(int(time())))
        self.temp_dir = os.path.join(
            config.plugins.tvmagazinecockpit.temp_dir.value, self.date_str)
        Picture.__init__(self, self.temp_dir)
        self.data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
        self.data_source = data_sources[config.plugins.tvmagazinecockpit.data_source.value]
        self.bouquet = getCurrentBouquetName(session)

        self.events = {}
        self.list_columns = []
        self.list_indices = []
        self.page_channel_list = []
        self.prime_event_indices = []
        self.timestamp = 0

        self.navigation = Navigation(self)
        self.column_handler = Column(self)
        self.page_handler = Page(self)

        self["key_red"] = StaticText(_("More") + " ...")
        self["key_green"] = StaticText(_("20:15"))
        self["key_yellow"] = StaticText(_("22:00"))
        self["key_blue"] = StaticText(_("Now"))

        for i in range(COLS):
            self["list%s" % i] = EventList(
                None, "ProgramColumns", "screenpart_program_template.tpl")
            self["channel%s" % i] = Label()
            self["picon%s" % i] = Pixmap()
            self["programpix%s" % i] = Pixmap()
            self["time%s" % i] = Label()
            self["description%s" % i] = Label()

        self["day_selector"] = Label()

        self["actions"] = ActionMap(
            ["TVC_Actions", "NumberActions"],
            {
                "0": self.reload,
                "ok": self.key_ok,
                "cancel": self.close,
                "info": self.key_ok,
                "up": self.moveUp,
                "down": self.moveDown,
                "left": self.left,
                "right": self.right,
                "next": self.key_next,
                "back": self.key_back,
                "red": self.key_red,
                "green": self.key_green,
                "yellow": self.key_yellow,
                "blue": self.key_blue,
                "menu": self.key_menu,
                "channelup": self.channelup,
                "channeldown": self.channeldown,
            }
        )

        self.first = True
        createDirectory(self.temp_dir)
        self.events = loadEvents()
        self.onClose.append(self.__onClose__)
        self.onLayoutFinish.append(self.reload)

    def showPage(self, events=None):
        """Display the current page of TV channels."""
        self.page_handler.showPage(events)

    def showColumn(self, events, service_ref, channel):
        """Display events for a specific channel in its designated column."""
        self.column_handler.showColumn(events, service_ref, channel)

    def left(self):
        self["list%s" % self.navigation.list_index].setSelectionEnable(False)
        refresh = self.navigation.left()
        self["list%s" % self.navigation.list_index].setSelectionEnable(True)
        if refresh:
            self.prime_event_indices = [-1] * COLS
            self.page_handler.showPage()

    def right(self):
        self["list%s" % self.navigation.list_index].setSelectionEnable(False)
        refresh = self.navigation.right()
        self["list%s" % self.navigation.list_index].setSelectionEnable(True)
        if refresh:
            self.prime_event_indices = [-1] * COLS  # Reset prime event indices
            self.page_handler.showPage()

    def moveUp(self):
        self.navigation.moveUp()
        self.page_handler.showPage()

    def moveDown(self):
        self.navigation.moveDown()
        self.page_handler.showPage()

    def channelup(self):
        self["list%s" % self.navigation.list_index].setSelectionEnable(False)
        self.navigation.channelup()
        self.prime_event_indices = [-1] * COLS  # Reset prime event indices
        self["list%s" % self.navigation.list_index].setSelectionEnable(True)
        self.page_handler.showPage()

    def channeldown(self):
        self["list%s" % self.navigation.list_index].setSelectionEnable(False)
        self.navigation.channeldown()
        self.prime_event_indices = [-1] * COLS  # Reset prime event indices
        self["list%s" % self.navigation.list_index].setSelectionEnable(True)
        self.page_handler.showPage()

    def key_next(self):
        self.navigation.key_next()
        self.reload()

    def key_back(self):
        self.navigation.key_back()
        self.reload()

    def key_ok(self):
        logger.info("...")
        current_selection = self["list%s" %
                                 self.navigation.list_index].l.getCurrentSelection()
        if current_selection:
            logger.debug("current_selection: %s", current_selection)
            service_ref = self.page_channel_list[self.navigation.list_index]
            channel_id = self.channel_dict.get(
                service_ref, {}).get(self.data_source_id, "")
            detailed_event = self.tvmagazine_data.getDetailedEvent(
                current_selection)
            if detailed_event:
                self.session.open(EventDetails, self.date_str,
                                  detailed_event, service_ref, channel_id)

    def key_red(self):
        logger.info("...")
        service_ref = self.page_channel_list[self.navigation.list_index]
        current_selection = self["list%s" %
                                 self.navigation.list_index].l.getCurrentSelection()
        self.openMore(service_ref, current_selection)

    def key_green(self):
        logger.info("...")
        self.timestamp = self.navigation.getTimestamp("20:15")
        self.page_handler.showPage()

    def key_yellow(self):
        logger.info("...")
        self.timestamp = self.navigation.getTimestamp("22:00")
        self.page_handler.showPage()

    def key_blue(self):
        logger.info("...")
        self.timestamp = self.navigation.getTimestamp(strftime("%H:%M"))
        self.page_handler.showPage()

    def key_menu(self):
        logger.info("...")
        self.openMenu()

    def clearColumn(self, i):
        logger.info("i: %s", i)
        self["list%s" % i].l.setList([])
        self["channel%s" % i].setText("")
        self["picon%s" % i].instance.setPixmap(None)
        self["programpix%s" % i].instance.setPixmap(None)
        self["time%s" % i].setText("")
        self["description%s" % i].setText("")

    def reload(self):
        logger.info("self.channel_list: %s", self.channel_list)
        self["list%s" % self.navigation.list_index].setSelectionEnable(False)
        self.channel_dict = readChannelDict()
        self.channel_list = readChannelList(self.channel_dict)
        self.navigation.reload(len(self.channel_list))
        self.data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
        self.data_source = data_sources[config.plugins.tvmagazinecockpit.data_source.value]
        self.timestamp = self.navigation.getTimestamp("20:15")
        self["day_selector"].setText(
            strftime("< %A, %d. %b %Y >", localtime(self.navigation.day_int)))
        self.list_columns = [[] for _i in range(COLS)]
        self.list_indices = [-1] * COLS
        self.prime_event_indices = [-1] * COLS
        self["list%s" % self.navigation.list_index].setSelectionEnable(True)
        self.page_handler.showPage()

    def __onClose__(self):
        logger.info("...")
