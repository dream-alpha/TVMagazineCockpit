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
from time import strftime, localtime
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Components.AVSwitch import AVSwitch
from Tools.Directories import pathExists
from Tools.LoadPixmap import LoadPixmap
from Downloader import headers_gzip, MydownloadPage, MyDeferredSemaphore, http_failed
from enigma import eServiceReference, ePicLoad
from StreamPlayer import StreamPlayer
from .Debug import logger
from .Constants import TMP_DIR, TVS, EVENT_IDX_SUBLINE, EVENT_IDX_EPISODE_TITLE, EVENT_IDX_YEAR, EVENT_IDX_VIDEOS, EVENT_IDX_IMAGES, EVENT_IDX_TITLE, EVENT_IDX_TIME_START, EVENT_IDX_TIME_END, EVENT_IDX_TEXT
from .PictureUtils import getPicon, getVideo, getEventPicUrl
from .__init__ import _


class EventDetails(Screen):
	def __init__(self, session, channel, list_event):
		logger.info("...")
		self.list_event = list_event
		self.channel = channel
		Screen.__init__(self, session)
		self.skinName = "EventDetails"
		self["description"] = ScrollLabel()
		self["actions"] = ActionMap(
			["TVC_Actions"],
			{
				"ok": self.key_ok,
				"cancel": self.close,
				"up": self["description"].pageUp,
				"left": self["description"].pageUp,
				"down": self["description"].pageDown,
				"right": self["description"].pageDown
			}
		)
		self["programpix"] = Pixmap()
		self["videopix"] = Pixmap()
		self["channelpix"] = Pixmap()
		self["daumenpix"] = Pixmap()

		self["title"] = Label()
		self["episodetitle"] = Label()
		self["timeduration"] = Label()

		self.picload = ePicLoad()
		self.picload_conn = self.picload.PictureData.connect(self.__finish_decode)
		self.deferreds = []
		self.download = MyDeferredSemaphore(tokens=12)

		self.onClose.append(self.__onClose__)
		self.onLayoutFinish.append(self.createsetup)

	def createsetup(self):
		logger.info("...")
		logger.debug("list_event: %s", self.list_event)
		self.setTitle("%s - %s" % (TVS, _("Event Details")))
		year = self.list_event[EVENT_IDX_YEAR]
		# genre = self.list_event[EVENT_IDX_GENRE]
		title = self.list_event[EVENT_IDX_TITLE]
		if year:
			title += " (%s)" % year
		self["title"].setText(title)
		episodetitle = self.list_event[EVENT_IDX_EPISODE_TITLE]
		subline = self.list_event[EVENT_IDX_SUBLINE]
		self["episodetitle"].setText(episodetitle if episodetitle else subline)
		start = strftime("%H:%M", localtime(int(self.list_event[EVENT_IDX_TIME_START])))
		duration = (int(self.list_event[EVENT_IDX_TIME_END]) - int(self.list_event[EVENT_IDX_TIME_START])) / 60
		self["timeduration"].setText("%s, %s %s" % (start, duration, _("min")))
		self["channelpix"].setPixmap(getPicon(self.channel["id"], self.channel["service"]))
		self["description"].setText(self.list_event[EVENT_IDX_TEXT])

		url = getEventPicUrl(self.list_event[EVENT_IDX_IMAGES])
		if url:
			afile = os.path.join(TMP_DIR, "programpix%s" % url[-4:])
			self.download.run(MydownloadPage, url, afile, headers=headers_gzip).addCallback(self.result_back_pic, self["programpix"], afile).addErrback(http_failed)

		self.video_title, url, self.video_url = getVideo(self.list_event[EVENT_IDX_VIDEOS])
		if url:
			afile = os.path.join(TMP_DIR, "videopix%s" % url[-4:])
			self.download.run(MydownloadPage, url, afile, headers=headers_gzip).addCallback(self.result_back_pic2, self["videopix"], afile).addErrback(http_failed)

	def result_back_pic(self, result, pixmap, afile):
		logger.info("result: %s", result)
		logger.info("afile: %s", afile)
		pixmap.instance.setPixmap(LoadPixmap(afile))

	def result_back_pic2(self, result, pixmap, afile):
		logger.info("result: %s", result)
		logger.info("afile: %s", afile)
		self.loadscalePixmap(pixmap, afile)

	def loadscalePixmap(self, pixmap, afile=""):
		logger.info("afile: %s, pixmap: %s", afile, pixmap)
		if pathExists(afile):
			# pixmap.instance.setPixmap(gPixmapPtr())
			scale = AVSwitch().getFramebufferScale()
			size = pixmap.instance.size()
			self.picload.setPara(
				(size.width(), size.height(), scale[0], scale[1], False, 1, "#00000000")
			)
			self.picload.startDecode(afile)

	def __finish_decode(self, _picInfo):
		logger.info("...")
		ptr = self.picload.getData()
		if ptr is not None:
			self["videopix"].instance.setPixmap(ptr)

	def deferCanceler(self):
		logger.info("...")
		for items in self.deferreds:
			if items.paused >= 0:
				items.pause()
			if not items.called:
				items.cancel()
			self.deferreds.remove(items)

	def key_ok(self):
		logger.info("...")
		if self.video_url and self.video_url.endswith(("mp4")):
			sref = eServiceReference(eServiceReference.idGST, 0, self.video_url)
			sref.setName(self.video_title)
			self.session.open(StreamPlayer, sref)

	def __onClose__(self):
		logger.info("...")
		del self.picload_conn
		del self.picload
		self.deferCanceler()
