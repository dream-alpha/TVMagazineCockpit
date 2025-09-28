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


import re
import json
from time import strftime, localtime
from .Debug import logger
from .Index import idx


# Category mapping
category = {
    'SP': 'Spielfilm',
    'SE': 'Serie',
    'RE': 'Report',
    'U': 'Unterhaltung',
    'KIN': 'Kinder',
    'SPO': 'Sport',
    'AND': 'Nachrichten'
}

# Regex patterns for base page parsing
html_data_val_com = re.compile(
    '<tr class="hover">.+?class="editorial-rating.+?</table>.+?</div>', re.S)
masterval_com = re.compile(
    '<tr class="hover">.+?class="editorial-rating.+?"></span></td>', re.S)
data_rel_start_com = re.compile(r'data-rel-start="(.+?)"', re.S)
data_rel_end_com = re.compile(r'data-rel-end="(.+?)"', re.S)
data_tracking_point_com = re.compile(
    r'<span>'  # Opening span tag
    # URL of the program (urlsendung)
    r'.+?<a href="(?P<url>http.+?html)"'
    r'.+?saveRef.+?'  # saveRef function call
    # Title attribute containing full title + subtitle
    r'title="(?P<full_title>.+?)"'
    # Extract raw JSON from data-tracking-point
    r'.+?data-tracking-point=\'(?P<data_tracking_point>.*?)\''
    r'.+?<strong>(?P<title>.+?)</strong>'  # The display title
    r'.+?</a>(?P<info>.*?)</span>', re.S  # Additional info after title
)

# Regex patterns for details page parsing
sectionidcontent_con_com = re.compile(
    r'<div class="content-area">.+?="inline-section_images"', re.S)
sectionidcontent_alt_com = re.compile(
    r'<div class="content-area">(.*?)<aside class="aside">', re.S)
xymatic_video_com = re.compile(
    r'"xymatic-video".+?"contentDesc": "(.+?)".+?http.+?key=(.+?)"', re.S)
og_image_com = re.compile(r'og:image" content="(.+?)" />', re.S)
descriptionre_com = re.compile(
    r'<section class="broadcast-detail__description">(.*?)</section>', re.S)
descriptionreg_com = re.compile(r'<p>(.*?)</p>', re.S)
episode_title_com = re.compile(r'<h2 class="broadcast-info">(.*?)</h2>', re.S)


def tvs_parse(html_data):
    """Parse base TV program listing data from HTML"""

    result = []
    html_data_val = html_data_val_com.search(html_data)

    if not html_data_val:
        return result

    masterval = masterval_com.findall(html_data_val.group())

    for master_item in masterval:
        logger.debug("master_item: %s", master_item)
        event = [None] * (len(idx) + 1)

        tmp = data_tracking_point_com.search(master_item, re.S)
        if tmp:

            # logger.debug("***********************************")
            # for name in tmp.groupdict():
            #     logger.debug("group %s: %s", name, tmp.group(name))

            event[idx['urlsendung']] = tmp.group('url')
            display_title = tmp.group('title')
            event[idx['title']] = display_title

            # Extract subtitle from full title
            event[idx['subtitle']] = ""
            full_title = tmp.group('full_title')
            if full_title.startswith(display_title):
                subtitle = full_title[len(display_title):].strip()
                if subtitle:
                    subtitle = subtitle.split(",")[0].strip()
                    event[idx["subtitle"]] = subtitle

            logger.debug("full_title: %s", full_title)
            full_title_parts = full_title.split(",")
            full_title = full_title_parts[0].strip(
            ) if full_title_parts else ""

            country_year = ""
            if len(full_title_parts) > 2:
                country_year = full_title_parts[2].strip()
            elif len(full_title_parts) > 1:
                country_year = full_title_parts[1].strip()
            event[idx['year']] = country_year

            if tmp.group('data_tracking_point'):
                tracking_data = json.loads(tmp.group('data_tracking_point'))
                logger.debug("tracking_data: %s", tracking_data)

                # Extract values directly from the parsed data
                event[idx['has_video']] = bool(
                    int(tracking_data.get('videoIntegration', 0)))
                event[idx['genre']] = tracking_data.get('genre', '')
                event[idx['category']] = tracking_data.get('category1', '')
                event[idx['channel']] = tracking_data.get('channel', '')

        endTime = startTime = 0
        tmp = data_rel_start_com.search(master_item, re.S)
        if tmp:
            startTime = int(tmp.group(1))
            event[idx['startTime']] = startTime
            event[idx['startHM']] = strftime("%H:%M", localtime(startTime))
        tmp = data_rel_end_com.search(master_item, re.S)
        if tmp:
            endTime = int(tmp.group(1))
            event[idx['endTime']] = endTime

        event[idx['duration']] = (endTime - startTime) / 60

        result.append(event)

        # for i, value in enumerate(event):
        #     logger.debug("event %s: %s", i, value)
    return result


def tvs_parse_details(html_data, event):
    """Parse details page for a specific TV program"""
    logger.info("Parsing details for event: %s", event[idx['urlsendung']])
    sectionidcontent_con_val = sectionidcontent_con_com.search(html_data)
    if not sectionidcontent_con_val:
        sectionidcontent_con_val = sectionidcontent_alt_com.search(html_data)
    # Generic fallback: if no section found, set all expected fields to defaults and return early
    if not sectionidcontent_con_val:
        event[idx['video_url']] = ""
        event[idx['photo_url']] = ""
        event[idx['description']] = ""
        event[idx['subtitle']] = ""
        return event

    # Extract video URL
    event[idx['video_url']] = ""
    xymatic_video_val = xymatic_video_com.search(
        sectionidcontent_con_val.group())
    if xymatic_video_val:
        event[idx['video_url']] = "https://media.delight.video/{0}/{1}/MEDIA/v0/HD/media.mp4".format(
            xymatic_video_val.group(2).strip(),
            xymatic_video_val.group(1).strip()
        )

    # Extract image
    event[idx['photo_url']] = ""
    og_image_val = og_image_com.search(html_data)
    if og_image_val:
        event[idx['photo_url']] = og_image_val.group(1).strip()

    # Extract description
    event[idx['description']] = ""
    descriptionre_val = descriptionre_com.search(html_data)
    if descriptionre_val:
        # Extract paragraphs directly
        event[idx['description']] = ""
        descriptionreg_val = descriptionreg_com.findall(
            descriptionre_val.group(1))
        if descriptionreg_val:
            for desval in descriptionreg_val:
                if desval:
                    event[idx['description']] += desval + "\n\n"

    # Extract episode subtitle/title from broadcast-info header
    episode_title_val = episode_title_com.search(html_data)
    if episode_title_val:
        subtitle_text = episode_title_val.group(1)
        if not subtitle_text.startswith("Mehr"):
            event[idx['subtitle']] = subtitle_text

    return event
