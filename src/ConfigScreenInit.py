#!/usr/bin/python
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
from .__init__ import _


class ConfigScreenInit():
	def __init__(self, _csel, session):
		self.session = session
		self.section = 400 * "¯"

		#        config list entry
		#                                                           , config element
		#                                                           ,                                                               , function called on save
		#                                                           ,                                                               ,                       , function called if user has pressed OK
		#                                                           ,                                                               ,                       ,                       , usage setup level from E2
		#                                                           ,                                                               ,                       ,                       ,   0: simple+
		#                                                           ,                                                               ,                       ,                       ,   1: intermediate+
		#                                                           ,                                                               ,                       ,                       ,   2: expert+
		#                                                           ,                                                               ,                       ,                       ,       , depends on relative parent entries
		#                                                           ,                                                               ,                       ,                       ,       ,   parent config value < 0 = true
		#                                                           ,                                                               ,                       ,                       ,       ,   parent config value > 0 = false
		#                                                           ,                                                               ,                       ,                       ,       ,             , context sensitive help text
		#                                                           ,                                                               ,                       ,                       ,       ,             ,
		#        0                                                  , 1                                                             , 2                     , 3                     , 4     , 5           , 6
		self.config_list = [
			(self.section                                       , _("COCKPIT")                                                  , None                  , None                  , 0     , []          , ""),
			(_("Default bouquet")                               , config.plugins.tvmagazinecockpit.bouquet                      , None                  , None                  , 0     , []          , _("Select the default bouquet.")),
			(_("Picon directory")                               , config.usage.configselection_piconspath                       , self.validatePath     , None                  , 0     , []          , _("Select the directory the picons are stored in.")),
			(self.section                                       , _("DEBUG")                                                    , None                  , None                  , 2     , []          , ""),
			(_("Log level")                                     , config.plugins.piconcockpit.debug_log_level                   , self.setLogLevel      , None                  , 2     , []          , _("Select the debug log level.")),
		]

	@staticmethod
	def save(_conf):
		logger.debug("...")

	def openLocationBox(self, element):
		logger.debug("element: %s", element.value)
		return True

	def setLogLevel(self, element):
		logger.debug("element: %s", element.value)
		return True

	def validatePath(self, element):
		logger.debug("element: %s", element.value)
		return True
