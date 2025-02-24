# -*- coding: utf-8 -*-

"""
    Exodus Add-on
    Copyright (C) 2016 Viper2k4

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import re
import urllib
import urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['netzkino.de']
        self.base_link = 'http://netzkino.de'
        self.conf_link = '/adconf/android-new.php'
        self.search_link = 'http://api.netzkino.de.simplecache.net/capi-2.0a/search?q=%s&d=www&l=de-DE&v=unknown-debugBuild'

    def movie(self, imdb, title, localtitle, year):
        try:
            url = self.__search(title, imdb, year)
            if not url and title != localtitle: url = self.__search(localtitle, imdb, year)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            r = client.request(urlparse.urljoin(self.base_link, self.conf_link), XHR=True)
            r = json.loads(r).get('streamer')
            r = client.request(r + '%s.mp4/master.m3u8' % url, XHR=True)

            r = re.findall('RESOLUTION\s*=\s*\d+x(\d+).*?\n(http.*?)(?:\n|$)', r, re.IGNORECASE)

            links = [(x[1], '4K') for x in r if int(x[0]) >= 2160]
            links += [(x[1], '1440') for x in r if int(x[0]) >= 1440]
            links += [(x[1], '1080p') for x in r if int(x[0]) >= 1080]
            links += [(x[1], 'HD') for x in r if 720 <= int(x[0]) < 1080]
            links += [(x[1], 'SD') for x in r if int(x[0]) < 720]

            for link, quality in links:
                sources.append({'source': 'CDN', 'quality': quality, 'language': 'de', 'url': link, 'direct': True, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, title, imdb, year):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query(title)))
            query = urlparse.urljoin(self.base_link, query)

            t = cleantitle.get(title)
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query, XHR=True)
            r = json.loads(r)

            r = [(i.get('title'), i.get('custom_fields', {})) for i in r.get('posts', [])]
            r = [(i[0], i[1]) for i in r if i[0] and i[1]]
            r = [(i[0], i[1].get('Streaming', ['']), i[1].get('Jahr', ['0']), i[1].get('IMDb-Link', [''])) for i in r if i]
            r = [(i[0], i[1][0], i[2][0], re.findall('.+?(tt\d+).*?', i[3][0])) for i in r if i[0] and i[1] and i[2] and i[3]]
            r = [i[1] for i in r if imdb in i[3] or (t == cleantitle.get(i[0]) and i[2] in y)][0]

            url = client.replaceHTMLCodes(r)
            url = url.encode('utf-8')
            return url
        except:
            return
