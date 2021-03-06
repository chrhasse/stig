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

from ..base import torrent as base
from . import _mixin as mixin
from .. import (ExpectedResource, InitCommand)
from ._common import make_tab_title_widget

from functools import partial


class ListTorrentsCmd(base.ListTorrentsCmdbase,
                      mixin.select_torrents,
                      mixin.create_list_widget):
    provides = {'tui'}

    def make_tlist(self, tfilter, sort, columns):
        from ...tui.views.torrentlist import TorrentListWidget
        self.create_list_widget(TorrentListWidget, theme_name='torrentlist',
                                tfilter=tfilter, sort=sort, columns=columns,
                                markable_items=True)
        return True


class TorrentSummaryCmd(base.TorrentSummaryCmdbase,
                        mixin.select_torrents, mixin.make_request):
    provides = {'tui'}
    tui = ExpectedResource

    async def display_summary(self, tfilter):
        if tfilter.needed_keys == ('id',):
            # If the filter is looking exclusively for IDs, we assume that it
            # specifies either a bunch of marked torrents or a focused torrent
            # in a list.  Since we can't show a summary for multiple torrents,
            # ignore the marks and pick the focused torrent.
            torrent_id = self.get_focused_torrent_id()
        else:
            # The user specified an arbitrary filter (e.g. 'summary foo|bar')
            # that we have to apply to get an ID.
            # Pick the first matching torrent.
            torrent = await self.get_torrent(tfilter, keys=('id',))
            if torrent is None:
                return False
            else:
                torrent_id = torrent['id']

        make_titlew = partial(make_tab_title_widget,
                              attr_unfocused='tabs.torrentsummary.unfocused',
                              attr_focused='tabs.torrentsummary.focused')

        from ...tui.views.summary import TorrentSummaryWidget
        TorrentSummaryWidget_keymapped = self.tui.keymap.wrap(TorrentSummaryWidget,
                                                              context='torrent')
        title_str = self.title if hasattr(self, 'title') else None
        summaryw = TorrentSummaryWidget_keymapped(self.srvapi, torrent_id, title=title_str)
        tabid = self.tui.tabs.load(make_titlew(summaryw.title), summaryw)

        def set_tab_title(text):
            # set_title() throws IndexError if the tab was removed, which may
            # have happened while TorrentSummaryWidget was waiting for a
            # response.
            try:
                self.tui.tabs.set_title(make_titlew(text), position=tabid)
            except IndexError:
                pass
        summaryw.title_updater = set_tab_title

        return True


class AddTorrentsCmd(base.AddTorrentsCmdbase,
                     mixin.polling_frenzy, mixin.make_request):
    provides = {'tui'}


class MoveTorrentsCmd(base.MoveTorrentsCmdbase,
                      mixin.polling_frenzy, mixin.make_request, mixin.select_torrents):
    provides = {'tui'}


class RemoveTorrentsCmd(base.RemoveTorrentsCmdbase,
                        mixin.polling_frenzy, mixin.make_request, mixin.select_torrents,
                        mixin.ask_yes_no):
    provides = {'tui'}
    cmdmgr = ExpectedResource
    CONFIRMATION_TAB_TITLE = "Removal Confirmation"

    async def show_list_of_hits(self, tfilter):
        cmd = 'tab --title %r ls --sort name %s' % (self.CONFIRMATION_TAB_TITLE, tfilter)
        await self.cmdmgr.run_async(cmd)

    async def remove_list_of_hits(self):
        cmd = 'tab --close %r --focus left' % self.CONFIRMATION_TAB_TITLE
        await self.cmdmgr.run_async(cmd)

class StartTorrentsCmd(base.StartTorrentsCmdbase,
                       mixin.polling_frenzy, mixin.make_request, mixin.select_torrents):
    provides = {'tui'}


class StopTorrentsCmd(base.StopTorrentsCmdbase,
                      mixin.polling_frenzy, mixin.make_request, mixin.select_torrents):
    provides = {'tui'}


class VerifyTorrentsCmd(base.VerifyTorrentsCmdbase,
                        mixin.make_request, mixin.select_torrents):
    provides = {'tui'}
