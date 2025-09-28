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


from Plugins.Plugin import PluginDescriptor
from .ConfigInit import ConfigInit
from .SkinUtils import loadPluginSkin
from .Debug import logger
from .Version import VERSION
from . import _
from .TVMagazineCockpit import TVMagazineCockpit
from .Cache import Cache


cache_instance = None


def main(session, **__kwargs):
    logger.info("...")
    session.open(TVMagazineCockpit)


def autoStart(reason, **kwargs):
    global cache_instance
    if reason == 0:  # startup
        if "session" in kwargs:
            logger.info("+++ Version: %s starts...", VERSION)
            loadPluginSkin("skin.xml")
            cache_instance = Cache()
            cache_instance.cleanup()
            cache_instance.downloadEvents()
    elif reason == 1:  # shutdown
        logger.info("--- shutdown")
        cache_instance = None


def Plugins(**__kwargs):
    ConfigInit()
    return [
        PluginDescriptor(
            where=[
                PluginDescriptor.WHERE_AUTOSTART,
                PluginDescriptor.WHERE_SESSIONSTART
            ],
            fnc=autoStart
        ),
        PluginDescriptor(
            name="TVMagazineCockpit",
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon="TVMagazineCockpit.png",
            description=_("Browse TV Magazine"),
            fnc=main
        ),
    ]
