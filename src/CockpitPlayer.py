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


from Components.ActionMap import ActionMap
from Screens.MoviePlayer import MoviePlayer
from Screens.InfoBarGenerics import InfoBarServiceErrorPopupSupport
from .Debug import logger


class CockpitPlayer(MoviePlayer, InfoBarServiceErrorPopupSupport):
    def __init__(self, session, service):
        logger.info("...")
        MoviePlayer.__init__(self, session, service, askBeforeLeaving=False)
        InfoBarServiceErrorPopupSupport.__init__(self)
        InfoBarServiceErrorPopupSupport.STATE_TUNING = ""
        InfoBarServiceErrorPopupSupport.STATE_CONNECTING = ""
        InfoBarServiceErrorPopupSupport.MESSAGE_WAIT = ""
        InfoBarServiceErrorPopupSupport.STATE_RECONNECTING = ""
        self.skinName = "MoviePlayer"

        self["ShowHideActions"] = ActionMap(
            ["InfobarShowHideActions"],
            {
                "cancel": self.leavePlayer,
            },
            1
        )

    def show(self):
        # disable the info bar
        logger.info("...")
