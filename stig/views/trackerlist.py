# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details
# http://www.gnu.org/licenses/gpl-3.0.txt

"""TUI and CLI specs for tracker list columns"""

from ..logging import make_logger
log = make_logger(__name__)

from . import ColumnBase


COLUMNS = {}
ALIASES = { 'host'   : 'domain',
            'u-an'   : 'url-announce',
            'u-sc'   : 'url-scrape',
            'e-an'   : 'error-announce',
            'e-sc'   : 'error-scrape',
            'l-an'   : 'last-announce',
            'n-an'   : 'next-announce',
            'l-sc'   : 'last-scrape',
            'n-sc'   : 'next-scrape',
            'dns'    : 'downloads',
            'status' : 'state' }


class TorrentName(ColumnBase):
    header = {'left': 'Torrent'}
    align = 'left'
    width = None
    min_width = 7
    may_have_wide_chars = True

    def get_value(self):
        return self.data['tname']

COLUMNS['torrent'] = TorrentName


class Tier(ColumnBase):
    header = {'left': 'Tier'}
    align = 'right'
    width = 4
    min_width = 4

    def get_value(self):
        return self.data['tier']

COLUMNS['tier'] = Tier


class Domain(ColumnBase):
    header = {'left': 'Domain'}
    align = 'left'
    width = None
    min_width = 5

    def get_value(self):
        return self.data['domain']

COLUMNS['domain'] = Domain


class AnnounceURL(ColumnBase):
    header = {'left': 'Announce'}
    align = 'left'
    width = None
    min_width = 10

    def get_value(self):
        return self.data['url-announce']

COLUMNS['url-announce'] = AnnounceURL


class ScrapeURL(ColumnBase):
    header = {'left': 'Scrape'}
    align = 'left'
    width = None
    min_width = 10

    def get_value(self):
        return self.data['url-scrape']

COLUMNS['url-scrape'] = ScrapeURL


class State(ColumnBase):
    header = {'left': 'State'}
    align = 'right'
    width = 10
    min_width = 5

    def get_value(self):
        return self.data['state']

COLUMNS['state'] = State


class Error(ColumnBase):
    header = {'left': 'Error'}
    align = 'left'
    width = None
    min_width = 20

    def get_value(self):
        return self.data['error']

COLUMNS['error'] = Error


class ErrorAnnounce(ColumnBase):
    header = {'left': 'Announce Error'}
    align = 'left'
    width = None
    min_width = 10

    def get_value(self):
        return self.data['error-announce']

COLUMNS['error-announce'] = ErrorAnnounce


class ErrorScrape(ColumnBase):
    header = {'left': 'Scrape Error'}
    align = 'left'
    width = None
    min_width = 10

    def get_value(self):
        return self.data['error-scrape']

COLUMNS['error-scrape'] = ErrorScrape


class Downloads(ColumnBase):
    header = {'left': 'Downloads'}
    align = 'right'
    width = 9
    min_width = 5

    def get_value(self):
        return self.data['count-downloads']

    def get_raw(self):
        return int(self.get_value())

COLUMNS['downloads'] = Downloads


class Leeches(ColumnBase):
    header = {'left': 'Leeches'}
    align = 'right'
    width = 7
    min_width = 5

    def get_value(self):
        return self.data['count-leeches']

    def get_raw(self):
        return int(self.get_value())

COLUMNS['leeches'] = Leeches


class Seeds(ColumnBase):
    header = {'left': 'Seeds'}
    align = 'right'
    width = 5
    min_width = 5

    def get_value(self):
        return self.data['count-seeds']

    def get_raw(self):
        return int(self.get_value())

COLUMNS['seeds'] = Seeds


class LastAnnounce(ColumnBase):
    header = {'left': 'Last Announce'}
    align = 'right'
    width = 13
    min_width = 10

    def get_value(self):
        return self.data['time-last-announce']

COLUMNS['last-announce'] = LastAnnounce


class NextAnnounce(ColumnBase):
    header = {'left': 'Next Announce'}
    align = 'right'
    width = 13
    min_width = 10

    def get_value(self):
        return self.data['time-next-announce']

COLUMNS['next-announce'] = NextAnnounce


class LastScrape(ColumnBase):
    header = {'left': 'Last Scrape'}
    align = 'right'
    width = 11
    min_width = 10

    def get_value(self):
        return self.data['time-last-scrape']

COLUMNS['last-scrape'] = LastScrape


class NextScrape(ColumnBase):
    header = {'left': 'Next Scrape'}
    align = 'right'
    width = 11
    min_width = 10

    def get_value(self):
        return self.data['time-next-scrape']

COLUMNS['next-scrape'] = NextScrape
