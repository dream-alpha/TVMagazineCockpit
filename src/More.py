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
from Components.UsageConfig import preferredTimerPath
from RecordTimer import RecordTimerEntry
from Screens.TimerEdit import TimerSanityConflict
from Screens.TimerEntry import TimerEntry
from Screens.ChoiceBox import ChoiceBox
from enigma import eServiceReference
from ServiceReference import ServiceReference
from .__init__ import _
from .Debug import logger
from .Version import PLUGIN
from .ZapUtils import zapService
from .Constants import EVENT_IDX_TIME_START, EVENT_IDX_TIME_END, EVENT_IDX_TITLE, EVENT_IDX_GENRE
from .PluginUtils import getPlugin, WHERE_MEDIATHEK_SEARCH, WHERE_TMDB_MOVIELIST
from .ServiceUtils import getService


class More():
	def __init__(self):
		logger.info("...")
		self.mediathek_plugin = getPlugin(WHERE_MEDIATHEK_SEARCH)
		self.tmdb_plugin = getPlugin(WHERE_TMDB_MOVIELIST)

	def openMore(self, service, event):
		logger.info("service: %s", service)
		logger.info("event: %s", event)
		self.service = service
		self.event = event
		alist = [
			("%s" % _("Zap"), "zap"),
			("%s" % _("Add Timer"), "timer"),
		]
		if self.mediathek_plugin:
			alist.append(("%s" % self.mediathek_plugin.description, "mediathek_search"))
		if self.tmdb_plugin:
			alist.append(("%s" % self.tmdb_plugin.description, "tmdb_search"))

		self.session.openWithCallback(
			self.openMoreCallback,
			ChoiceBox,
			title=PLUGIN,
			list=alist,
			windowTitle=_("More"),
			allow_cancel=True,
			titlebartext=_("Input")
		)

	def openMoreCallback(self, answer=None):
		logger.info("...")
		if answer:
			action = answer[1]
			if action == "zap":
				zapService(self.service)
				self.close()
			elif action == "timer":
				serviceref = ServiceReference(eServiceReference(self.service))
				begin = int(self.event[EVENT_IDX_TIME_START]) - config.recording.margin_before.value * 60
				end = int(self.event[EVENT_IDX_TIME_END]) + config.recording.margin_after.value * 60
				eventdata = (begin, end, self.event[EVENT_IDX_TITLE], self.event[EVENT_IDX_GENRE], None)
				newEntry = RecordTimerEntry(serviceref, checkOldTimers=True, dirname=preferredTimerPath(), *eventdata)
				self.session.openWithCallback(self.finishedAdd, TimerEntry, newEntry)
			elif action == "mediathek_search":
				self.mediathek_plugin(self.session, self.event[EVENT_IDX_TITLE])
			elif action == "tmdb_search":
				service = getService("", self.event[EVENT_IDX_TITLE])
				self.tmdb_plugin(self.session, service)

	def finishedAdd(self, answer):
		logger.info("...")
		if answer[0]:
			entry = answer[1]
			simulTimerList = self.session.nav.RecordTimer.record(entry)
			if simulTimerList is not None:
				for x in simulTimerList:
					if x.setAutoincreaseEnd(entry):
						self.session.nav.RecordTimer.timeChanged(x)
				simulTimerList = self.session.nav.RecordTimer.record(entry)
				if simulTimerList is not None:
					self.session.openWithCallback(self.finishedAdd, TimerSanityConflict, simulTimerList)
		else:
			logger.debug("Timeredit aborted")
