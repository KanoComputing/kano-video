from gi.repository import Gtk

from .ui_elements import TopBar, VideoListLocal, VideoListYoutube, SearchBar


class View(Gtk.EventBox):
    _VIEW_HEIGHT = 400

    def __init__(self):
        Gtk.EventBox.__init__(self)

        self._grid = Gtk.Grid()
        self._grid.set_row_spacing(10)
        self._grid.set_size_request(-1, self._VIEW_HEIGHT)

        align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        padding = 20
        align.set_padding(padding, padding, padding, padding)
        align.add(self._grid)

        self.add(align)


class LocalView(View):

    def __init__(self):
        View.__init__(self)

        self._header = TopBar('Test')
        self._grid.attach(self._header, 0, 0, 1, 1)

        self._list = VideoListLocal()
        self._grid.attach(self._list, 0, 1, 1, 1)


class YoutubeView(View):

    def __init__(self):
        View.__init__(self)

        self._header = SearchBar(self._search)
        self._grid.attach(self._header, 0, 0, 1, 1)

        self._list = VideoListYoutube()
        self._grid.attach(self._list, 0, 1, 1, 1)

    def _search(self, _button, search_keyword_entry=None, list_by_username=None):
        if search_keyword_entry and search_keyword_entry.get_text():
            self._grid.remove(self._list)
            self._list = VideoListYoutube(keyword=search_keyword_entry.get_text())
            self._grid.add(self._list)

        elif list_by_username and list_by_username.get_text():
            self._grid.remove(self._list)
            self._list = VideoListYoutube(username=list_by_username.get_text())
            self._grid.add(self._list)


class PlaylistView(View):

    def __init__(self):
        View.__init__(self)
