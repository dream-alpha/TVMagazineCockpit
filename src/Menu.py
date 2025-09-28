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
from Screens.ChoiceBox import ChoiceBox
from Components.config import config
from .__init__ import _
from .Debug import logger
from .ConfigScreen import ConfigScreen
from .About import about
from .Version import PLUGIN
from .FileUtils import deleteDirectory, createDirectory
from .ConfigInit import COLS


class Menu():
    def __init__(self, session):
        logger.info("...")
        self.session = session
        self.temp_dir = config.plugins.tvmagazinecockpit.temp_dir.value
        self.data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"

    def openMenu(self):
        logger.info("...")
        alist = [
            (_("Settings"), "settings"),
            (_("About"), "about"),
        ]

        self.session.openWithCallback(
            self.openMenuCallback,
            ChoiceBox,
            title=PLUGIN,
            list=alist,
            windowTitle=_("Menu"),
            allow_cancel=True,
            titlebartext=_("Input")
        )

    def openMenuCallback(self, answer=None):
        logger.info("...")
        if answer:
            screen = answer[1]
            if screen == "settings":
                self.session.openWithCallback(
                    self.openConfigScreenCallback,
                    ConfigScreen,
                    config.plugins.tvmagazinecockpit
                )
            elif screen == "about":
                about(self.session)

    def openConfigScreenCallback(self, changed=False):
        logger.info("changed: %s", changed)
        if changed:
            prev_temp_dir = os.path.dirname(self.temp_dir)
            logger.debug("Previous temp directory: %s", prev_temp_dir)
            self.temp_dir = os.path.join(
                config.plugins.tvmagazinecockpit.temp_dir.value, self.date_str)
            logger.debug("New temp directory: %s", self.temp_dir)
            if self.data_source_id != config.plugins.tvmagazinecockpit.data_source.value + "_id":
                self.data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
                logger.debug("Data source ID changed to: %s",
                             self.data_source_id)
                for i in range(COLS):
                    self.clearColumn(i)
                deleteDirectory(prev_temp_dir)
                createDirectory(self.temp_dir)
                self.events = {}
            self.reload()
