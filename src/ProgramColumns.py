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


import os
import time
from datetime import datetime
from time import strftime, localtime
from math import ceil
from enigma import gPixmapPtr
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.config import config
from Tools.LoadPixmap import LoadPixmap
from .Downloader import headers_gzip, MydownloadPage, http_failed, MyDeferredSemaphore
from .EventDetails import EventDetails
from .More import More
from .Menu import Menu
from .__init__ import _
from .EventList import EventList
from .Debug import logger
from .TVSpielfilmData import TVSpielfilmData
from .Constants import TMP_DIR, TVS, BOUQUETS, EVENT_IDX_YEAR, EVENT_IDX_IMAGES, EVENT_IDX_TITLE, EVENT_IDX_EPISODE_TITLE, EVENT_IDX_SUBLINE, EVENT_IDX_TIME_START, EVENT_IDX_BROADCASTER_NAME
from .PictureUtils import getEventPicUrl, getPicon
from .FileUtils import deleteDirectory
from .ChannelUtils import read_channel_list


class ProgramColumns(Screen, More, Menu):
	def __init__(self, session, channel_dict):
		logger.info("...")
		self.bouquet = config.plugins.tvmagazinecockpit.bouquet.value
		self.channel_list = read_channel_list(self.bouquet)
		self.channel_dict = channel_dict
		Screen.__init__(self, session)
		self.skinName = "ProgramColumns"
		More.__init__(self)
		Menu.__init__(self)
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
				"menu": self.showMenu,
				"channelup": self.channelup,
				"channeldown": self.channeldown,
			}
		)

		self.tvs_data_mgr = TVSpielfilmData(self.showChannel)
		self.events = {}
		self.cols = 6
		self.list_columns = [[]] * self.cols
		self.list_prime = [[]] * self.cols
		self.list_indices = [-1] * self.cols
		self.listindex = 0
		self.page_index = 0
		self.pages = 0

		self["searchdate"] = Label()

		for i in range(self.cols):
			self["list%s" % i] = EventList(None, "ProgramColumns", "screenpart_program_template.tpl")
			self["channel%s" % i] = Label()
			self["channelpix%s" % i] = Pixmap()
			self["programpix%s" % i] = Pixmap()
			self["time%s" % i] = Label()
			self["description%s" % i] = Label()

		self.first = True
		self.mytimecount = 1
		mytime = int(time.time()) - 24 * 60 * 60
		self.timelist = []
		for _day in range(0, 15):
			self.timelist.append([strftime("< %A, %d. %b %Y >", localtime(mytime)), strftime("%Y-%m-%d", localtime(mytime))])
			mytime = mytime + 24 * 60 * 60

		self["key_red"] = StaticText(_("More") + " ...")
		self["key_green"] = StaticText(_("20:15"))
		self["key_yellow"] = StaticText(_("22:00"))
		self["key_blue"] = StaticText(_("Now"))

		self.download = MyDeferredSemaphore(tokens=100)
		self.onClose.append(self.__onClose__)
		self.onLayoutFinish.append(self.reload)

	def downloadChannel(self, channel, i):
		logger.info("channel: %s", channel)
		if self.channel_list:
			self.tvs_data_mgr.downloadEvents(channel, self.day, i)
		else:
			self.showPage()

	def showPage(self):
		logger.info("...")
		# logger.info("self.events: %s", self.events)
		title = "%s %s - %s: %s" % (TVS, _("column view"), BOUQUETS[self.bouquet], _("Loading..."))
		self.setTitle(title)
		self.clearValues()
		start = self.page_index * 6
		stop = min(start + 6, len(self.channel_list))
		self.page_list = self.channel_list[start:stop]
		logger.debug("page_list: %s", self.page_list)

		for i, channel_name in enumerate(self.page_list):
			channel = self.channel_dict.get(channel_name, None)
			if channel:
				channel_id = channel["id"]
				self["channel%s" % i].setText(channel_id)
				# self["description%s" % i].setText(_("no event info avilable"))
				if self.day in self.events and channel_id in self.events[self.day]:
					logger.debug("data already available")
					self.showChannel(self.events, channel, i)
				else:
					logger.debug("need to download data")
					self.downloadChannel(channel, i)
		if len(self.page_list) == 0:
			title = "%s %s - %s: %s: %s/%s, %s: %s" % (TVS, _("column view"), BOUQUETS[self.bouquet], _("Page"), self.page_index + 1, self.pages, _("Services"), len(self.channel_list))
			self.setTitle(title)

	def showChannel(self, events, channel, i):

		def createListEntry(event):
			entry = []
			start_time = strftime("%H:%M", localtime(int(event[EVENT_IDX_TIME_START])))
			entry.append(start_time)
			entry.append(event[EVENT_IDX_TITLE])
			sub_title = event[EVENT_IDX_EPISODE_TITLE]
			if not sub_title:
				sub_title = event[EVENT_IDX_SUBLINE]
			entry.append(sub_title)
			entry.append(str(event[EVENT_IDX_YEAR]))
			entry.append(int(event[EVENT_IDX_TIME_START]))
			return entry

		logger.info("i: %s", i)
		channel_id = channel["id"]
		self.events = events
		tmp_list = []
		prime_time = self.getPointInTime("20:15")
		prime_diff = prime_time
		self.list_prime[i] = None
		now_time = self.point_in_time
		now_diff = now_time
		now_index = 0
		for event_index, event in enumerate(events[self.day][channel_id]):
			tmp = createListEntry(event)
			event_time = int(event[EVENT_IDX_TIME_START])
			event_diff = abs(prime_time - event_time)
			# logger.debug("event_time: %s, event_diff: %s, prime_diff: %s", event_time, event_diff, prime_diff)
			if event_diff < prime_diff:
				prime_diff = event_diff
				self.list_prime[i] = event
				# logger.debug("new prime diff: %s", prime_diff)

			event_diff = abs(now_time - event_time)
			# logger.debug("event_time: %s, event_diff: %s, now_diff: %s", event_time, event_diff, now_diff)
			if event_diff < now_diff:
				now_diff = event_diff
				now_index = event_index
				# logger.debug("new now diff: %s, index: %s", now_diff, now_index)
			tmp_list.append(tmp)

		if self.list_prime[i]:
			self.showPrimeEvent(self.list_prime[i], i, channel)

		self.list_columns[i] = tmp_list
		self.list_indices[i] = now_index

		sub_list = self.list_columns[i][self.list_indices[i] - 1:self.list_indices[i] + 4]
		j = len(sub_list)
		while j < 5:
			sub_list.append(["", "", "", "", 0])
			j += 1

		self["list%s" % i].l.setList(sub_list)
		self["list%s" % i].moveToIndex(1)
		if i == 0 and self.first:
			self.first = False
			self["list0"].setSelectionEnable(True)
		title = "%s %s - %s: %s: %s/%s, %s: %s" % (TVS, _("column view"), BOUQUETS[self.bouquet], _("Page"), self.page_index + 1, self.pages, _("Services"), len(self.channel_list))
		self.setTitle(title)

	def showPrimeEvent(self, prime_event, i, channel):
		logger.info("...")
		channel_id = channel["id"]
		self["channel%s" % i].setText(prime_event[EVENT_IDX_BROADCASTER_NAME])
		self["time%s" % i].setText(strftime("%H:%M", localtime(int(prime_event[EVENT_IDX_TIME_START]))))
		self["description%s" % i].setText(prime_event[EVENT_IDX_TITLE])
		self["channelpix%s" % i].instance.setPixmap(gPixmapPtr())
		self["channelpix%s" % i].instance.setPixmap(getPicon(channel_id, channel["service"]))
		url = getEventPicUrl(prime_event[EVENT_IDX_IMAGES])
		if url:
			afile = os.path.join(TMP_DIR, "programpix-%s-%s%s" % (self.day, channel_id, url[-4:]))
			if os.path.exists(afile):
				self.result_back_pic(None, i, afile)
			else:
				self.download.run(MydownloadPage, url, afile, headers=headers_gzip).addCallback(self.result_back_pic, i, afile).addErrback(http_failed)

	def result_back_pic(self, result, i, event_pic_file):
		logger.info("result: %s", result)
		logger.info("i: %s, event_pic_file: %s", i, event_pic_file)
		self["programpix%s" % i].instance.setPixmap(LoadPixmap(event_pic_file))

	def clearValues(self):
		logger.info("...")
		for i in range(self.cols):
			self["channel%s" % i].setText("")
			self["time%s" % i].setText("")
			self["description%s" % i].setText("")
			self["channelpix%s" % i].instance.setPixmap(gPixmapPtr())
			self["list%s" % i].l.setList([])
			self["programpix%s" % i].instance.setPixmap(gPixmapPtr())

	def left(self):
		logger.info("...")
		self["list%s" % self.listindex].setSelectionEnable(False)
		self.listindex -= 1
		if self.listindex < 0:
			self.listindex = self.cols - 1
			self.page_index -= 1
			if self.page_index < 0:
				self.page_index = self.pages - 1
				max_listindex = len(self.channel_list) % self.cols - 1
				if max_listindex >= 0:
					self.listindex = max_listindex
			self.showPage()
		self["list%s" % self.listindex].setSelectionEnable(True)

	def right(self):
		logger.info("...")
		self["list%s" % self.listindex].setSelectionEnable(False)
		max_listindex = len(self.channel_list) % self.cols - 1
		self.listindex += 1
		if (
			self.listindex > self.cols - 1
			or (self.page_index == self.pages - 1 and self.listindex > max_listindex)
		):
			self.listindex = 0
			self.page_index += 1
			if self.page_index > self.pages - 1:
				self.page_index = 0
			self.showPage()
		self["list%s" % self.listindex].setSelectionEnable(True)

	def moveUp(self):
		logger.info("listindex: %s", self.listindex)
		if self.list_indices[self.listindex] > 1:
			self.list_indices[self.listindex] -= 1
		index = self.list_indices[self.listindex]
		column = self.list_columns[self.listindex]
		self.point_in_time = column[index][4]
		sub_list = column[index - 1:index + 4]
		self["list%s" % self.listindex].setList(sub_list)
		self.showPage()

	def moveDown(self):
		logger.info("listindex: %s", self.listindex)
		logger.debug("index: %s, len(list): %s", self.list_indices[self.listindex], len(self.list_columns[self.listindex]))
		if self.list_indices[self.listindex] < len(self.list_columns[self.listindex]) - 1:
			self.list_indices[self.listindex] += 1
		index = self.list_indices[self.listindex]
		column = self.list_columns[self.listindex]
		self.point_in_time = column[index][4]
		sub_list = column[index - 1:index + 4]
		self["list%s" % self.listindex].setList(sub_list)
		self.showPage()

	def channelup(self):
		logger.info("...")
		self["list%s" % self.listindex].setSelectionEnable(False)
		self.page_index += 1
		if self.page_index >= self.pages:
			self.page_index = 0
		self.listindex = 0
		self["list%s" % self.listindex].setSelectionEnable(True)
		self.showPage()

	def channeldown(self):
		logger.info("...")
		self["list%s" % self.listindex].setSelectionEnable(False)
		self.page_index -= 1
		if self.page_index < 0:
			self.page_index = self.pages - 1
			self.listindex = self.cols - 1 if len(self.channel_list) % self.cols == 0 else len(self.channel_list) % self.cols - 1
		else:
			self.listindex = self.cols - 1
		self["list%s" % self.listindex].setSelectionEnable(True)
		self.showPage()

	def showMore(self):
		logger.info("...")
		if self.download.finished():
			self.openMore(self.bouquet, self.channel_list, self.channel_dict)

	def showMenu(self):
		if self.download.finished():
			channel_name = self.page_list[self.listindex]
			channel = self.channel_dict.get(channel_name, None)
			if channel:
				event = self.events[self.day][channel["id"]][self.list_indices[self.listindex]]
				self.openMenu(channel["service"], event)

	def key_next(self):
		logger.info("...")
		self.mytimecount += 1
		self.reload()

	def key_back(self):
		logger.info("...")
		self.mytimecount -= 1
		self.reload()

	def key_ok(self):
		logger.info("...")
		current_selection = self["list%s" % self.listindex].l.getCurrentSelection()
		if current_selection:
			logger.debug("current_selection: %s", current_selection)
			channel_name = self.page_list[self.listindex]
			channel_id = self.channel_dict[channel_name]["id"]
			self.session.open(
				EventDetails,
				self.channel_dict[channel_name],
				self.events[self.day][channel_id][self.list_indices[self.listindex]],
			)

	def getPointInTime(self, hm):
		logger.info("hm: %s", hm)
		logger.info("mytimecount: %s", self.mytimecount)
		ymd = self.timelist[self.mytimecount][1].split("-")
		hm = hm.split(":")
		point_in_time = int(datetime(int(ymd[0]), int(ymd[1]), int(ymd[2]), int(hm[0]), int(hm[1]), 0).strftime("%s"))
		logger.debug("point_in_time: %s", point_in_time)
		return point_in_time

	def key_red(self):
		logger.info("...")
		self.showMore()

	def key_green(self):
		logger.info("...")
		self.point_in_time = self.getPointInTime("20:15")
		self.showPage()

	def key_yellow(self):
		logger.info("...")
		self.point_in_time = self.getPointInTime("22:00")
		self.showPage()

	def key_blue(self):
		logger.info("...")
		self.point_in_time = self.getPointInTime(time.strftime("%H:%M"))
		self.showPage()

	def reload(self):
		logger.info("self.channel_list: %s", self.channel_list)
		self["list%s" % self.listindex].setSelectionEnable(False)
		self.pages = int(ceil(float(len(self.channel_list)) / self.cols))
		self.listindex = 0
		self.page_index = 0
		self.mytimecount = max(min(len(self.timelist) - 1, self.mytimecount), 0)
		self["searchdate"].text = self.timelist[self.mytimecount][0]
		self.day = self.timelist[self.mytimecount][1]
		self.list_columns = [[]] * self.cols
		self.list_prime = [[]] * self.cols
		self.list_indices = [-1] * self.cols
		self.point_in_time = self.getPointInTime("20:15")
		self["list%s" % self.listindex].setSelectionEnable(True)
		self.showPage()

	def __onClose__(self):
		logger.info("...")
		self.download.deferCanceler()
		del self.download.ds.waiting[:]
		self.download.work.clear()
		deleteDirectory(TMP_DIR)
