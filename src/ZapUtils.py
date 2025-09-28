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


from Screens.InfoBar import InfoBar
from Screens.ChannelSelection import service_types_tv
from enigma import eServiceCenter, eServiceReference
from .Debug import logger


def zapService(service_str):
    logger.info("service_str: %s", service_str)
    if service_str:
        service = eServiceReference(str(service_str))
        if service:
            allservice = eServiceReference(
                "%s ORDER BY name" % (service_types_tv))
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
                    if (currlist is not None) and (service_str in currlist.getContent("S", True)):
                        break
            if InfoBar.instance.servicelist.getRoot() != bouquet:  # already in correct bouquet?
                InfoBar.instance.servicelist.clearPath()
                if bouquet_root != bouquet:
                    InfoBar.instance.servicelist.enterPath(bouquet_root)
                InfoBar.instance.servicelist.enterPath(bouquet)
            InfoBar.instance.servicelist.setCurrentSelection(
                service)  # select the service in servicelist
            InfoBar.instance.servicelist.zap()
