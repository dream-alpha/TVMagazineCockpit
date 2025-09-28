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


import json
from time import strftime, localtime
from datetime import datetime, timedelta
from twisted.internet import threads, reactor
from .Debug import logger
from .UnicodeUtils import convertUni2Str
from .WebRequests import WebRequests
from .DateTimeUtils import datetime_to_epoch
from .Index import idx
from .CacheUtils import saveEvents


class TVMData(WebRequests):
    def __init__(self, channel_dict):
        WebRequests.__init__(self)
        self.channel_dict = channel_dict

    def parseEvent(self, broadcast):
        logger.debug("parseEvent: %s", broadcast)
        # Format datetime strings to epoch timestamps
        start_time = datetime_to_epoch(broadcast.get('airTime'))
        end_time = datetime_to_epoch(broadcast.get('airTimeEnd'))

        # Extract people information
        persons = broadcast.get('persons', [])
        cast = []
        director = []
        for person in persons:
            # logger.debug("person: %s", person)
            if isinstance(person, str):
                logger.debug("person is string: %s", person)
                person = {}
            name = person.get('name', '')
            function = person.get('function', '')
            if function == 'Darsteller':
                role = person.get('role', '')
                if role:
                    cast.append("{0} ({1})".format(name, role))
                else:
                    cast.append(name)
            elif function == 'Regie':
                director.append(name)

        # Get image URL if available
        photo_url = ""
        if 'previewImage' in broadcast and 'filepath' in broadcast['previewImage']:
            # Get the highest resolution image available
            filepath = broadcast['previewImage']['filepath']
            if 'android-image-640-360' in filepath:
                photo_url = filepath['android-image-640-360']
            elif 'ipad-image-variable-640' in filepath:
                photo_url = filepath['ipad-image-variable-640']

        startHM = strftime("%H:%M", localtime(start_time))

        # Build formatted event object

        formatted_event = [None] * (len(idx) + 1)

        formatted_event[idx['startHM']] = startHM
        formatted_event[idx['title']] = broadcast.get('title', '')
        formatted_event[idx['subtitle']] = broadcast.get('subTitle', '')
        formatted_event[idx['year']] = str(broadcast.get('productionYear', ''))
        formatted_event[idx['startTime']] = start_time
        formatted_event[idx['country']] = broadcast.get(
            'countryOfProduction', '')
        formatted_event[idx['category']] = ""
        formatted_event[idx['genre']] = ""
        formatted_event[idx['endTime']] = end_time
        formatted_event[idx['duration']] = broadcast.get(
            'bruttoLength', 0) / 60
        formatted_event[idx['channel']] = ""
        formatted_event[idx['urlsendung']] = ""
        formatted_event[idx['has_video']] = False
        formatted_event[idx['photo_url']] = photo_url
        formatted_event[idx['description']] = broadcast.get('text', '')
        formatted_event[idx['video_url']] = ""

        return formatted_event

    def downloadEvents(self, day, page_channel_list, all_events, callback):
        logger.info("page_channel_id_list: %s, day: %s",
                    page_channel_list, day)
        threads.deferToThread(self.downloading, day,
                              page_channel_list, all_events, callback)

    def downloading(self, day, page_channel_list, all_events, callback):
        logger.info("page_channel_list: %s, day: %s", page_channel_list, day)
        if day not in all_events:
            all_events[day] = {}

        page_channel_id_list = []
        channel_id2service_ref = {}
        for service_ref in page_channel_list:
            channel_id = self.channel_dict.get(
                service_ref, {}).get("tvm_id", "")
            channel_id2service_ref[channel_id] = service_ref
            page_channel_id_list.append(channel_id)
        channel_ids = ",".join(page_channel_id_list)

        date_obj = datetime.strptime(day, "%Y-%m-%d")
        next_day = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
        url = "http://capi.tvmovie.de/v1/broadcasts?channel=%s&date_from=%sT04:00:00&date_to=%sT04:00:00" % (
            channel_ids, day, next_day)
        logger.debug("url: %s", url)
        result = self.getContent(url)
        logger.info("result: %s", result)
        if result:
            channels = convertUni2Str(json.loads(result).get('channels', []))
            logger.debug("channels: %s", channels)
            for channel in channels:
                logger.debug("channel: %s", channel)
                channel_id = channel.get('id', "-1")
                logger.debug("channel_id: %s", channel_id)
                if channel_id in page_channel_id_list:
                    service_ref = channel_id2service_ref[channel_id]
                    if service_ref not in all_events[day]:
                        all_events[day][service_ref] = []
                    broadcasts = channel.get('broadcasts', [])
                    # logger.debug("broadcasts: %s", broadcasts)
                    for event in broadcasts:
                        logger.debug("event: %s", event)
                        parsed_event = self.parseEvent(event)
                        if parsed_event:
                            all_events[day][service_ref].append(parsed_event)
        saveEvents(all_events)
        reactor.callFromThread(callback, all_events)  # pylint: disable=E1101
