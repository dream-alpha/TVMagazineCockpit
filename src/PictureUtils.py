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


from Components.config import config
from Tools.LoadPixmap import LoadPixmap
from .Debug import logger


def getPicon(channel_id, service=""):
	logger.info("channel_id: %s, service: %s", channel_id, service)
	pixmap_ptr = None
	if service:
		picons_dir = config.usage.configselection_piconspath.value
		pixmap_ptr = LoadPixmap("%s/%s.png" % (picons_dir, service[:-1].replace(":", "_")))
	return pixmap_ptr


def getVideo(videos):
	logger.debug("videos: %s", videos)
	title = video_url = still_image_url = ""
	if len(videos) > 0:
		video_list = videos[0].get("video", "")
		video = video_list[0]
		logger.debug("video: %s", video)
		title = videos[0].get("title", "")
		still_image_url = videos[0].get("stillImage", "")
		video_url = video.get("url", "")
	logger.debug("title: %s, still_image_url: %s, video_url: %s", title, still_image_url, video_url)
	return title, still_image_url, video_url


def getEventPicUrl(images):
	logger.debug("images: %s", images)
	url = ""
	if len(images) > 0:
		image = images[0]
		url = image.get("size4", "")
		logger.debug("programpix url: %s", url)
	return url
