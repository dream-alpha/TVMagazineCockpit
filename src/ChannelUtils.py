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
import json
from six import text_type
from Tools.Directories import resolveFilename, SCOPE_CONFIG, pathExists
from .ConfigInit import plugindir
from .Debug import logger


def convert_unicode_to_str(input_data):
	if isinstance(input_data, dict):
		return {convert_unicode_to_str(key): convert_unicode_to_str(value) for key, value in input_data.iteritems()}
	if isinstance(input_data, list):
		return [convert_unicode_to_str(element) for element in input_data]
	if isinstance(input_data, text_type):
		return input_data.encode("utf-8")
	return input_data


def read_channel_list(bouquet="default"):
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
			channel_list = convert_unicode_to_str(json.load(data_file))
	logger.debug("channel_list: %s", channel_list)
	return channel_list


def write_channel_list(bouquet, channel_list):
	logger.info("bouquet: %s", bouquet)
	channel_list_filename = "tvspielfilm_channel_list_%s.json" % bouquet
	path = os.path.join(resolveFilename(SCOPE_CONFIG), channel_list_filename)
	with open(path, "w") as afile:
		json.dump(channel_list, afile, indent=2)


def read_channel_dict():
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
			channel_dict = convert_unicode_to_str(json.load(data_file))
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
