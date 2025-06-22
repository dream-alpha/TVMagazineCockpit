#!/usr/bin/python
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
from twisted.internet import threads, reactor
from enigma import ePicLoad, gPixmapPtr
from Components.AVSwitch import AVSwitch
from Tools.BoundFunction import boundFunction
from .Debug import logger
from .WebRequests import WebRequests


class Picture(WebRequests):
    def __init__(self, temp_dir):
        WebRequests.__init__(self)
        self.temp_dir = temp_dir
        self.sc = AVSwitch().getFramebufferScale()
        self.picload_cache = {}
        self.picload_conn_cache = {}

    def showPicture(self, pixmap, atype, ident, url):
        logger.info("atype: %s, ident: %s, url: %s", atype, ident, url)
        path = os.path.join(self.temp_dir, atype + str(ident) + ".jpg")
        if url and not url.endswith("None") and not os.path.isfile(path):
            threads.deferToThread(self.downloadPicture,
                                  pixmap, url, path, self.displayPicture)
        else:
            self.displayPicture(pixmap, path)

    def downloadPicture(self, pixmap, url, path, callback):
        logger.info("path: %s", path)
        self.downloadFile(url, path)
        logger.debug("downloaded: %s", path)
        reactor.callFromThread(callback, pixmap, path)  # pylint: disable=E1101

    def displayPicture(self, pixmap, path):
        logger.info("path: %s", path)
        if os.path.isfile(path):
            if path not in self.picload_cache:
                self.picload_cache[path] = ePicLoad()
            picload = self.picload_cache[path]
            if path not in self.picload_conn_cache:
                self.picload_conn_cache[path] = picload.PictureData.connect(
                    boundFunction(self.onPictureReady, path, pixmap))
            picload_conn = self.picload_conn_cache[path]  # pylint: disable=W0612
            picload.setPara(
                (
                    pixmap.instance.size().width(),
                    pixmap.instance.size().height(),
                    self.sc[0], self.sc[1],
                    False,
                    1,
                    "#ff000000"
                )
            )
            picload.startDecode(path)  # Asynchronous call
        else:
            logger.error("pixmap not found: %s", path)
            pixmap.instance.setPixmap(gPixmapPtr())

    def onPictureReady(self, path, pixmap, _picInfo=""):
        logger.info("...")
        ptr = self.picload_cache[path].getData()
        if ptr is not None:
            pixmap.instance.setPixmap(ptr)
        else:
            pixmap.instance.setPixmap(gPixmapPtr())
        self.picload_cache.pop(path, None)
        self.picload_conn_cache.pop(path, None)
