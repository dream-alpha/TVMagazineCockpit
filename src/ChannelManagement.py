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


import re
from APIs.ServiceData import getTVBouquets, getServiceList
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
# from Screens.MessageBox import MessageBox
from Screens.ChannelSelection import service_types_tv
from Screens.SimpleSummary import SimpleSummary
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from ServiceReference import ServiceReference
from Tools.Directories import resolveFilename, SCOPE_CONFIG
from .__init__ import _
from .MyList import MyList
from .Debug import logger
from .ChannelUtils import writeChannelList, getChannel
from .Constants import TVS
from .ZapUtils import zapService


class ChannelManagement(Screen):
	def __init__(self, session, bouquet, channel_list, channel_dict):
		logger.info("...")
		self.bouquet = bouquet
		self.channel_list = channel_list
		self.channel_list_org = channel_list[:]
		logger.debug("channel_list: %s", self.channel_list)
		self.channel_dict = channel_dict
		Screen.__init__(self, session)
		self.skinName = "ChannelManagement"
		self["actions"] = ActionMap(
			["TVC_Actions"],
			{
				"ok": self.key_ok,
				"cancel": self.key_red,
				"red": self.key_red,
				"green": self.key_green,
				"yellow": self.key_yellow,
				"blue": self.key_blue,
				# "info": self.showInfo,
				"menu": self.showMenu,
				# "menulong": self.showMenuLong
			}
		)
		self["actionsmove"] = ActionMap(
			["TVC_Actions"],
			{
				"up": self.keyUp,
				"down": self.keyDown,
				"left": self.noop,
				"right": self.noop
			}
		)
		self["actionsmove"].setEnabled(False)

		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText()
		self["key_yellow"] = StaticText(_("TV Bouquets"))
		self["key_blue"] = StaticText(_("Bouquets"))

		self["list"] = MyList()
		self["list"].style = "default"
		self.mytitlestr = ("mytitle1", "mytitle2", "mytitle3", "mytitle4", "mytitle5")
		self["mytitle1"] = Label("TV Spielfilm Name")
		self["mytitle2"] = Label("TV Spielfilm ID")
		self["mytitle3"] = Label("Enigma Name")
		self["mytitle4"] = Label(_("Service Reference"))
		self["mytitle5"] = Label(_("Favorites"))
		for myx in self.mytitlestr:
			self[myx].hide()
		self["message"] = Label()
		self.listtype = ""
		self.bouquet_list = []
		self.key_blue()

	def createBouquetList(self, channel_list, channel_dict):
		result = []
		for channel_name in channel_list:
			channel_id = channel_dict[channel_name]["id"]
			value = channel_dict[channel_name]
			if value:
				enameval = ""
				ename = ServiceReference(value["service"]).getServiceName()
				if not ename:
					enameval = _("not found")
				elif value["ename"] != ename:
					enameval = ename
				result.append([value["tname"], channel_id, value["ename"], value["service"], enameval, channel_name])
			else:
				result.append(["n/a", channel_id, "n/a", "n/a", ""])
		return result

	def noop(self):
		logger.info("...")

	def keyUp(self):
		logger.info("...")
		if self.listtype in "blue":
			currindex = self["list"].getIndex()
			self["list"].moveSelection("moveUp")
			self["list"].list.insert(self["list"].getIndex(), self["list"].list.pop(currindex))

	def keyDown(self):
		logger.info("...")
		if self.listtype in "blue":
			currindex = self["list"].getIndex()
			self["list"].moveSelection("moveDown")
			self["list"].list.insert(self["list"].getIndex(), self["list"].list.pop(currindex))

	def key_red(self):
		logger.info("...")
		self.close(self.channel_list_org)

	def key_green(self):
		logger.info("...")
		if self.listtype == "blue":
			channel_list = []
			bouquet_channel_list = self["list"].getList()
			for list_element in bouquet_channel_list:
				channel_list.append(list_element[5])
			writeChannelList(self.bouquet, channel_list)
			logger.debug("channel_list: %s", channel_list)
			self.close(channel_list)

	def key_yellow(self):

		def channels_file_name(bouquet):
			return resolveFilename(SCOPE_CONFIG, "tvspielfilm_%s_channels.json" % bouquet)

		logger.info("...")
		self.listtype = "yellow"
		self.setTitle(self["key_yellow"].text)
		self["key_green"].text = ""
		self["actionsmove"].setEnabled(False)
		tvbouquets = getTVBouquets()
		mylist = []
		allname = self.cleanname("Alle Sender (Enigma)")
		filenameall = channels_file_name(allname)
		mylist.append(["Alle Sender (Enigma)", "", service_types_tv, allname, filenameall, "eall"])
		for bouquet in tvbouquets:
			name = self.cleanname(bouquet[1])
			filename = channels_file_name(name)

			mylist.append([bouquet[1], "", bouquet[0], name, filename, "bouq"])
		for myx in self.mytitlestr:
			self[myx].hide()
		self["list"].style = "default"
		self["list"].setList(mylist)
		title = "%s %s - %s: %s" % (TVS, _("Channel Management"), _("TV Bouquets"), self["list"].count())
		self.setTitle(title)
		self["message"].setText(_("Press OK for channel list"))

	def key_blue(self):
		logger.info("...")
		self["actionsmove"].setEnabled(False)
		self.listtype = "blue"
		self.setTitle(self["key_blue"].text)
		self["key_green"].text = _("Save")
		for myx in self.mytitlestr:
			self[myx].show()
		self["mytitle5"].text = _("name difference")
		self["list"].style = "channel_bouquet"
		self.bouquet_list = self.createBouquetList(self.channel_list, self.channel_dict)
		self["list"].updateList(self.bouquet_list)

		title = "%s %s - %s: %s" % (TVS, _("Channel Management"), _("Bouquet"), self.bouquet)
		self.setTitle(title)
		self["message"].setText(_("Press OK to enable/disable move function or Menu for more options"))

	def showMenu(self):
		logger.info("...")
		self["actionsmove"].setEnabled(False)
		selection = 0
		options = []
		mytitle = _("Select")
		curr = self["list"].getCurrent()
		if self.listtype == "blue":
			if curr:
				options.append((_("Delete channel"), "delcurr"))
				if self.bouquet_list:
					options.append((_("Delete all channels"), "delall"))
				options.append((_("Zap"), "zap"))
				mytitle = _("Bouquet")
		elif self.listtype == "yellow2":
			if curr:
				options.append((_("Add channel"), "addcurr"))
				options.append((_("Add all channels"), "addall"))
				mytitle = _("Channels (TV)")
		if options:
			self.session.openWithCallback(
				self.menuCallback,
				ChoiceBox,
				title=mytitle,
				list=options,
				selection=selection
			)

	def menuCallback(self, answer):
		logger.info("...")
		answer = answer and answer[1]
		curr = self["list"].getCurrent()
		if curr:
			if answer == "delcurr":
				self.channel_list.remove(curr[5])
				self["list"].deleteEntry()
				self.key_blue()
			elif answer == "delall":
				self.channel_list = []
				self.key_blue()
			elif answer == "addcurr":
				if self.addTVChannel(curr):
					self.key_blue()
			elif answer == "addall":
				self.channel_list = []
				for row in self["list"].getList():
					self.addTVChannel(row)
				logger.debug("addall: channel_list: %s", self.channel_list)
				self.key_blue()
			elif answer == "zap":
				zapService(curr[3])

	def addTVChannel(self, curr):
		name = curr[0]
		service = curr[1]
		channel_name = getChannel(service, self.channel_dict)
		if channel_name:
			self.channel_list.append(channel_name)
		else:
			logger.error("service not found: %s: %s", name, service)
		return True

	def key_ok(self):
		logger.info("...")
		curr = self["list"].getCurrent()
		if self.listtype == "yellow":
			if curr:
				self.showBouquetChannels(curr)
		elif self.listtype == "yellow2":
			self.addTVChannel(curr)
		elif self.listtype == "blue":
			if curr:
				if self["actionsmove"].enabled is False:
					self["actionsmove"].setEnabled(True)
					title = "%s %s - %s: %s - %s" % (TVS, _("Channel Management"), _("Bouquet"), self.bouquet, _("Move mode enabled"))
				else:
					self["actionsmove"].setEnabled(False)
					title = "%s %s - %s: %s" % (TVS, _("Channel Management"), _("Bouquet"), self.bouquet)
				self.setTitle(title)

	def showBouquetChannels(self, curr):
		logger.info("...")
		if curr:
			servicetypes = curr[2] + " ORDER BY name"
			service_list = getServiceList(servicetypes)
			logger.debug("service_list: %s", service_list)
			if service_list:
				mylist = []
				for service, ename in service_list:
					if "::" not in service:
						mylist.append((ename, service, ""))
		self.listtype = "yellow2"
		self["actionsmove"].setEnabled(False)
		for myx in self.mytitlestr:
			self[myx].hide()
		self["list"].style = "default"
		self["list"].setList(mylist)
		title = "%s %s - %s: %s" % (TVS, _("Channel Management"), _("TV Bouquet Channels"), self["list"].count())
		self.setTitle(title)
		self["message"].setText(_("Press OK to add channel, or Menu for more options"))

	def cleanname(self, msg):
		logger.info("...")
		p = re.compile("[^a-zA-Z0-9]")
		return p.sub("_", msg).replace(" ", "")

	def createSummary(self):
		logger.info("...")
		return SimpleSummary
