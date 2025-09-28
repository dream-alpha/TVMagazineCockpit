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
from time import time, strftime, localtime
import json
from Components.config import config
from .UnicodeUtils import convertUni2Str
from .Debug import logger


date_str = strftime("%Y-%m-%d", localtime(int(time())))


def loadEvents():
    logger.info("Loading events...")
    events = {}
    cache_path = os.path.join(
        config.plugins.tvmagazinecockpit.temp_dir.value, date_str, "events.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as fp:
            events = convertUni2Str(json.load(fp))
            logger.info("Events loaded successfully.")
            logger.debug("Loaded events: %s", events)
    else:
        logger.warning("Events cache file does not exist: %s", cache_path)
    return events


def saveEvents(events):
    logger.info("Saving events: %s", events)
    cache_path = os.path.join(
        config.plugins.tvmagazinecockpit.temp_dir.value, date_str, "events.json")
    if date_str in events:
        with open(cache_path, 'w') as fp:
            json.dump(events, fp, indent=4)
            logger.info("Events saved successfully to %s", cache_path)
