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


from __init__ import _

TMP_DIR = "tmp/TVC"
TVS = "TV Spielfilm"
BOUQUETS = {"default": _("default"), "favorites": _("favorites"), "sky": _("sky"), "all": _("all")}

EVENT_IDX_TIME_START = 0
EVENT_IDX_VIDEOS = 1
EVENT_IDX_IS_NEW = 2
EVENT_IDX_TEXT = 3
EVENT_IDX_GENRE = 4
EVENT_IDX_YEAR = 5
EVENT_IDX_IMAGES = 6
EVENT_IDX_CURRENT_TOPICS = 7
EVENT_IDX_ID = 8
EVENT_IDX_TITLE = 9
EVENT_IDX_EPISODE_TITLE = 10
EVENT_IDX_SUBLINE = 11
EVENT_IDX_TIME_END = 12
EVENT_IDX_REPEAT = 13
EVENT_IDX_BROADCASTER_ID = 14
EVENT_IDX_BROADCASTER_NAME = 15
EVENT_IDX_IS_TIP_OF_THE_DAY = 16
EVENT_IDX_IS_TOP_TIP = 17
EVENT_IDX_ANCHOR_MAN = 18
EVENT_IDX_THUMB_ID_NUMERIC = 19
EVENT_LENGTH = 20

EVENT_KEYS = [
	"timestart",
	"videos",
	"isNew",
	"text",
	"genre",
	"year",
	"images",
	"currentTopics",
	"id",
	"title",
	"episodeTitle",
	"subline",
	"timeend",
	"repeatHint",
	"broadcasterId",
	"broadcasterName",
	"isTipOfTheDay",
	"isTopTip",
	"anchorMan",
	"thumbIdNumeric"
]
