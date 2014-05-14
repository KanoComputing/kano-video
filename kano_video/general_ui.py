from gi.repository import Gtk


class KanoWidget(Gtk.EventBox):

    def __init__(self):
        super(KanoWidget, self).__init__(hexpand=True)

        self._grid = Gtk.Grid()
        self._grid.set_row_spacing(10)
        self._grid.set_column_spacing(10)
        self._grid.set_size_request(400, 30)

        self.add(self._grid)


class Spacer(Gtk.Label):

    def __init__(self):
        super(Spacer, self).__init__()

        spacer_str = '|'
        self.set_label(spacer_str)


class Contents(Gtk.ScrolledWindow):

    def __init__(self, win):
        super(Contents, self).__init__(hexpand=True, vexpand=True)

        self.get_style_context().add_class('contents')

        self.props.margin_top = 20
        self.props.margin_bottom = 20
        self.props.margin_left = 20
        self.props.margin_right = 12

        self._current = None
        self._box = Gtk.Box(hexpand=True, vexpand=True)
        self.add_with_viewport(self._box)

        self._win = win

    def get_window(self):
        return self._win

    def set_contents(self, obj):
        for w in self._box.get_children():
            self._box.remove(w)

        obj.props.margin_right = 10
        Gtk.Container.add(self._box, obj)
        self._show_all(obj)

    def _show_all(self, w):
        w.show()
        if hasattr(w, '__iter__'):
            for c in w:
                self._show_all(c)
