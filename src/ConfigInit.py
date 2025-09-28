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


from Components.config import config, ConfigSelection, ConfigSubsection, ConfigNothing, NoSave
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_CONFIG
from .Debug import logger, log_levels, initLogging

COLS = 6
ROWS = 5

plugindir = resolveFilename(SCOPE_PLUGINS, "Extensions/TVMagazineCockpit/")
configdir = resolveFilename(SCOPE_CONFIG)


data_sources = {
    "tvfa": "TVFürAlle",
    "tvm": "TVMovie",
    "tvs": "TVSpielfilm"
}

data_source_choices = list(data_sources.items())


class ConfigInit():

    def __init__(self):
        logger.info("...")
        config.plugins.tvmagazinecockpit = ConfigSubsection()
        config.plugins.tvmagazinecockpit.fake_entry = NoSave(ConfigNothing())
        config.plugins.tvmagazinecockpit.debug_log_level = ConfigSelection(
            default="INFO", choices=list(log_levels.keys()))
        config.plugins.tvmagazinecockpit.temp_dir = ConfigSelection(
            default="/data/TVC", choices=[("/data/TVC", "/data/TVC")])
        config.plugins.tvmagazinecockpit.data_source = ConfigSelection(
            default="tvfa", choices=data_source_choices)
        initLogging()
