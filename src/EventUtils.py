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


from .Debug import logger
from .Index import idx


def find_time_event_index(events, timestamp):
    """
    Find event closest to the specified time point.

    Args:
        events: List of events to search
        timestamp: Reference timestamp to find closest event to

    Returns:
        Event object or index, depending on return_event parameter
    """
    if not events:
        logger.debug("No input events")
        return -1

    closest_index = 0
    min_time_diff = float('inf')

    for index, event in enumerate(events):
        event_time = event[idx["startTime"]]
        time_diff = abs(timestamp - event_time)
        if time_diff < min_time_diff:
            min_time_diff = time_diff
            closest_index = index

    logger.debug("Found closest event at index %s with time difference %s",
                 closest_index, min_time_diff)
    return closest_index
