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


from Components.HTMLComponent import HTMLComponent
from Components.TemplatedMultiContentComponent import TemplatedMultiContentComponent
from enigma import eListbox
from .SkinUtils import getSkinPath
from .FileUtils import readFile
from .Debug import logger


class EventList(HTMLComponent, TemplatedMultiContentComponent, object):

    COMPONENT_ID = ""
    default_template = ""

    def __init__(self, alist=None, component_id="", default_template_name=""):
        logger.info("...")
        self.skinAttributes = []
        EventList.default_template = readFile(
            getSkinPath(default_template_name))
        EventList.COMPONENT_ID = component_id
        TemplatedMultiContentComponent.__init__(self)
        self.list = alist if alist else []

    def getCurrent(self):
        logger.info("...")
        return self.l.getCurrentSelection()

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        logger.info("...")
        instance.setContent(self.l)

    def preWidgetRemove(self, instance):
        logger.info("...")
        instance.setContent(None)

    def moveToIndex(self, index):
        logger.info("...")
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        logger.info("...")
        return self.instance.getCurrentIndex()

    def moveUp(self):
        logger.info("...")
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveUp)

    def moveDown(self):
        logger.info("...")
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveDown)

    def moveLeft(self):
        logger.info("...")
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveLeft)

    def moveRight(self):
        logger.info("...")
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveRight)

    def invalidate(self):
        logger.info("...")
        self.l.invalidate()

    def entryRemoved(self, index):
        logger.info("...")
        self.l.entryRemoved(index)

    def setSelectionEnable(self, selectionEnabled=True):
        logger.info("...")
        self.instance.setSelectionEnable(selectionEnabled)
