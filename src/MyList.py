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


from Components.Sources.List import List
from .Debug import logger


class MyList(List):
	def __init__(self, alist=None, enableWrapAround=False, item_height=25, fonts=None, buildfunc=None):
		logger.info("...")
		if alist is None:
			alist = []
		if fonts is None:
			fonts = []
		List.__init__(self, list=alist, enableWrapAround=enableWrapAround, item_height=item_height, fonts=fonts, buildfunc=buildfunc)

	def extendList(self, alist):
		logger.info("...")
		self.list.extend(alist)
		self.changed((self.CHANGED_ALL, ))

	def sort(self, key=0):
		logger.info("...")
		self.list.sort(key=key)
		self.changed((self.CHANGED_ALL, ))

	def deleteEntry(self):
		logger.info("...")
		index = self.master.getIndex()
		del self.list[index]
		self.setList(self.list)
		self.master.setIndex(index)
		self.entry_changed(index)

	def clearList(self):
		logger.info("...")
		if self.list:
			del self.list[:]
			self.changed((self.CHANGED_CLEAR, ))

	def modifyEntryVal(self, index, data, indexval):
		self.list[index][indexval] = data
		self.entry_changed(index)

	def getList(self):
		return self.list[:]
