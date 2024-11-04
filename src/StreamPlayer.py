# !/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2024 by dream-alpha
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


from Screens.InfoBar import MoviePlayer
from Components.ActionMap import ActionMap
from .Debug import logger


class StreamPlayer(MoviePlayer):
	def __init__(self, session, service):
		logger.info("...")
		MoviePlayer.__init__(self, session, service)
		self.skinName = "MoviePlayer"
		if "CueSheetActions" in self:
			del self["CueSheetActions"]
		if "MenuActions" in self:
			del self["MenuActions"]
		if "MovieListActions" in self:
			del self["MovieListActions"]
		if "TeletextActions" in self:
			del self["TeletextActions"]
		if "InstantExtensionsActions" in self:
			del self["InstantExtensionsActions"]
		if "helpActions" in self:
			del self["helpActions"]
		if "EPGActions" in self:
			del self["EPGActions"]

		self["ShowHideActions"] = ActionMap(
			["InfobarShowHideActions"],
			{
				"toggleShow": self.toggleShow,
				"hide": self.leavePlayer,
			},
			1
		)

	def seekFwd(self):
		logger.info("...")

	def seekBack(self):
		logger.info("...")

	def handleLeave(self, _how):
		logger.info("...")
		self.close()
