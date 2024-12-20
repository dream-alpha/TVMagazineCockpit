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


import json
from .Downloader import headers_gzip, MygetPage, MyDeferredSemaphore
from .Constants import EVENT_KEYS, EVENT_IDX_VIDEOS, EVENT_IDX_IMAGES, EVENT_LENGTH
from .Debug import logger
from .UnicodeUtils import convertUni2Str


class TVSpielfilmData():
	def __init__(self, callback):
		self.callback = callback
		self.events = {}
		self.download = MyDeferredSemaphore(tokens=32)

	def parseJsonEvents(self, json_events):
		logger.info("...")
		list_events = []
		for json_event in json_events:
			list_event = [""] * EVENT_LENGTH
			for index, key in enumerate(EVENT_KEYS):
				# logger.debug("json_event: %s", json_event)
				# logger.debug("index: %s, key: %s", index, key)
				if index in [EVENT_IDX_VIDEOS, EVENT_IDX_IMAGES]:
					# logger.debug("json_event: %s", json_event)
					list_event[index] = json_event.get(key, [])
				else:
					list_event[index] = json_event.get(key, "")
			list_events.append(list_event)
		return list_events

	def downloadEvents(self, channel, day, i):
		logger.info("channel: %s, day: %s", channel, day)
		channel_id = channel["id"]
		del self.download.ds.waiting[:]
		url = "https://live.tvspielfilm.de/static/broadcast/list/%s/%s" % (channel_id, day)
		logger.debug("url: %s", url)
		self.download.run(MygetPage, url, headers=headers_gzip).addCallback(self.result_back, channel, i, day).addErrback(self.download_failed, channel, i, day)

	def result_back(self, result, channel, i, day):
		logger.info("channel: %s", channel)
		channel_id = channel["id"]
		if result:
			if day not in self.events:
				self.events[day] = {}
			events = convertUni2Str(json.loads(result))
			self.events[day][channel_id] = self.parseJsonEvents(events)
		self.callback(self.events, channel, i)

	def download_failed(self, failure, channel, i, day):
		logger.error("channel: %s, failure: %s", channel, failure)
		self.events[day] = {}
		self.callback(self.events, channel, i)
