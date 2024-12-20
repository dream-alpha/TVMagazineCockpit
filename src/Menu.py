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


from Screens.ChoiceBox import ChoiceBox
from Components.config import config
from .__init__ import _
from .Debug import logger
from .ConfigScreen import ConfigScreen
from .ChannelManagement import ChannelManagement
from .ChannelUtils import readChannelList
from .ConfigInit import bouquet_choices
from .About import about
from .Version import PLUGIN


class Menu():
	def __init__(self):
		logger.info("...")

	def openMenu(self, bouquet, channel_list, channel_dict):
		logger.info("...")
		self.bouquet = bouquet
		self.channel_list = channel_list
		self.channel_dict = channel_dict
		alist = [
			("%s" % _("Bouquet Selection"), "bouquetselection"),
			("%s" % _("Bouquet Setup"), "channel"),
			("%s" % _("Settings"), "settings"),
			("%s" % _("About"), "about"),
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
			if screen == "channel":
				self.session.openWithCallback(
					self.openChannelManagementCallback,
					ChannelManagement,
					self.bouquet,
					self.channel_list,
					self.channel_dict,
				)
			elif screen == "settings":
				self.session.openWithCallback(
					self.openConfigScreenCallback,
					ConfigScreen,
					config.plugins.tvmagazinecockpit
				)
			elif screen == "bouquetselection":
				alist = [(value[1], value[0]) for value in bouquet_choices]
				self.session.openWithCallback(
					self.openBouquetSelectionCallback,
					ChoiceBox,
					title="Bouquet Selection",
					list=alist,
					windowTitle=_("Bouquet Selection"),
					allow_cancel=True,
					titlebartext=_("Input")
				)
			elif screen == "about":
				about(self.session)

	def openConfigScreenCallback(self, _result=None):
		logger.info("...")
		self.reload()

	def openChannelManagementCallback(self, channel_list):
		logger.info("...")
		self.channel_list = channel_list
		self.reload()

	def openBouquetSelectionCallback(self, bouquet):
		logger.info("bouquet: %s", bouquet)
		if bouquet:
			config.plugins.tvmagazinecockpit.bouquet.value = bouquet[1]
			config.plugins.tvmagazinecockpit.bouquet.save()
			self.bouquet = bouquet[1]
			self.channel_list = readChannelList(self.bouquet)
			self.reload()
