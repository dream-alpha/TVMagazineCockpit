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


from .Debug import logger
from .ProgramColumns import ProgramColumns
from .ChannelUtils import read_channel_dict
from .Constants import TMP_DIR
from .FileUtils import createDirectory


class TVMagazineCockpit():
	def __init__(self, session, **_kwargs):
		logger.info("...")
		self.session = session
		self.last_screen = None
		createDirectory(TMP_DIR)
		self.channel_dict = read_channel_dict()
		self.showScreenCallback("programcolumns")

	def showScreen(self, screen, *args):
		logger.info("screen: %s", screen)
		self.session.openWithCallback(self.showScreenCallback, screen, *args)

	def showScreenCallback(self, *args):
		return_screen = args[0] if len(args) > 0 else ""
		logger.info("return_screen: %s", return_screen)
		if return_screen == "programcolumns":
			self.showScreen(ProgramColumns, self.channel_dict)
