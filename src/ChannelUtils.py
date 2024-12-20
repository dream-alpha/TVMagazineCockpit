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
import json
from Tools.Directories import resolveFilename, SCOPE_CONFIG, pathExists
from .ConfigInit import plugindir
from .UnicodeUtils import convertUni2Str
from .Debug import logger


def readChannelList(bouquet="default"):
	logger.info("bouquet: %s", bouquet)
	filename = ""
	channel_list = []
	channel_list_filename = "tvspielfilm_channel_list_%s.json" % bouquet
	path = os.path.join(resolveFilename(SCOPE_CONFIG), channel_list_filename)
	if pathExists(path):
		filename = path
	else:
		path = os.path.join(plugindir, channel_list_filename)
		if pathExists(path):
			filename = path
	logger.debug("filename: %s", filename)
	if filename:
		with open(filename) as data_file:
			channel_list = convertUni2Str(json.load(data_file))
	logger.debug("channel_list: %s", channel_list)
	return channel_list


def writeChannelList(bouquet, channel_list):
	logger.info("bouquet: %s", bouquet)
	channel_list_filename = "tvspielfilm_channel_list_%s.json" % bouquet
	path = os.path.join(resolveFilename(SCOPE_CONFIG), channel_list_filename)
	with open(path, "w") as afile:
		json.dump(channel_list, afile, indent=2)


def readChannelDict():
	logger.info("...")
	filename = ""
	channel_dict = {}
	channel_dict_filename = "tvspielfilm_channel_dict_default.json"
	path = os.path.join(resolveFilename(SCOPE_CONFIG), channel_dict_filename)
	if pathExists(path):
		filename = path
	else:
		path = os.path.join(plugindir, channel_dict_filename)
		if pathExists(path):
			filename = path
	logger.debug("filename: %s", filename)
	if filename:
		with open(filename) as data_file:
			channel_dict = convertUni2Str(json.load(data_file))
	logger.debug("channel_dict: %s", channel_dict)
	return channel_dict


def getChannel(service, channel_dict):
	logger.info("service: %s", service)
	for channel_name, channel in channel_dict.iteritems():
		# logger.debug("channel_name: %s, channel: %s", channel_name, channel)
		if channel["service"] == service:
			logger.debug("found: %s", channel_name)
			break
	else:
		channel_name = ""
	logger.debug("channel_name: %s", channel_name)
	return channel_name
