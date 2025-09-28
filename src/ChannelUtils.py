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
from enigma import eServiceCenter, eServiceReference
from Screens.ChannelSelection import service_types_tv
from Screens.InfoBar import InfoBar
from Components.config import config
from APIs.ServiceData import getServiceList
from .ConfigInit import plugindir, configdir
from .UnicodeUtils import convertUni2Str
from .Debug import logger
from .__init__ import _


def getCurrentBouquet():
    last_root = config.tv.lastroot.value.split(";")
    bouquet = last_root[-2]
    logger.debug("bouquet: %s", bouquet)
    return bouquet


def getCurrentBouquetName(session):
    logger.info("...")
    bouquet_name = _("Unknown")
    service = session.nav.getCurrentlyPlayingServiceReference()
    if service:
        allservice = eServiceReference("%s ORDER BY name" % (service_types_tv))
        serviceHandler = eServiceCenter.getInstance()
        bouquet_root = InfoBar.instance.servicelist.bouquet_root
        bouquet = bouquet_root
        bouquetlist = serviceHandler.list(bouquet_root)
        if bouquetlist is not None:
            while True:
                bouquet = bouquetlist.getNext()
                if not bouquet.valid():
                    bouquet = allservice
                    break
                currlist = serviceHandler.list(bouquet)
                if (currlist is not None) and (service.toString() in currlist.getContent("S", True)):
                    # Get the bouquet name
                    info = serviceHandler.info(bouquet)
                    if info:
                        bouquet_name = info.getName(bouquet)
                    break
        logger.debug("Found service in bouquet: %s", bouquet_name)
    return bouquet_name


def getBouquetServices(bouquet, channel_dict):
    # Get the list of services (channels) in the bouquet
    service_list = getServiceList(bouquet)
    services = []
    for service, _name in service_list:
        channel = channel_dict.get(service, {})
        if "::" not in service and config.plugins.tvmagazinecockpit.data_source.value + "_id" in channel:
            services.append(service)
    logger.debug("services: %s", services)
    return services


def readChannelList(channel_dict):
    services = getBouquetServices(getCurrentBouquet(), channel_dict)
    return services


def readChannelDict():
    logger.info("...")
    channel_dict = {}
    channel_dict_filename = "tvc_channel_dict.json"
    dirs = [configdir, plugindir]
    for adir in dirs:
        path = os.path.join(adir, channel_dict_filename)
        if os.path.exists(path):
            with open(path) as data_file:
                channel_dict = convertUni2Str(json.load(data_file))
            break
    # logger.debug("channel_dict: %s", channel_dict)
    return channel_dict
