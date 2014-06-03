from gi.repository import Gtk, Gdk

from kano_video.paths import image_dir

from .icons import set_from_name


class KanoWidget(Gtk.EventBox):

    def __init__(self):
        super(KanoWidget, self).__init__(hexpand=True)

        self._grid = Gtk.Grid()
        self._grid.set_row_spacing(10)
        self._grid.set_column_spacing(0)
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


class TopBar(Gtk.EventBox):
    _TOP_BAR_HEIGHT = 44

    def __init__(self, title):
        super(TopBar, self).__init__(hexpand=True, vexpand=True)

        self.get_style_context().add_class('top_bar_container')

        box = Gtk.Box()
        box.set_size_request(-1, self._TOP_BAR_HEIGHT)

        self._header = Gtk.Label(title, halign=Gtk.Align.CENTER,
                                 valign=Gtk.Align.CENTER,
                                 hexpand=True)
        box.pack_start(self._header, True, True, 0)

        self._header.get_style_context().add_class('header')

        # Close button
        cross_icon = set_from_name('cross')

        self._close_button = Gtk.Button()
        self._close_button.set_image(cross_icon)
        self._close_button.props.margin_right = 2
        self._close_button.set_can_focus(False)
        self._close_button.get_style_context().add_class('top_bar_button')
        self._close_button.get_style_context().add_class('no_border')

        self._close_button.connect('clicked', self._close_button_click)
        self._close_button.connect('enter-notify-event',
                                   self._close_button_mouse_enter)
        self._close_button.connect('leave-notify-event',
                                   self._close_button_mouse_leave)

        box.pack_start(self._close_button, False, False, 0)

        self.add(box)

    def _close_button_mouse_enter(self, button, event):
        # Change the cursor to hour Glass
        cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
        self.get_root_window().set_cursor(cursor)

    def _close_button_mouse_leave(self, button, event):
        # Set the cursor to normal Arrow
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def _close_button_click(self, event):
        self.get_toplevel().destroy()


class RemoveButton(Gtk.Button):

    def __init__(self):
        super(RemoveButton, self).__init__()

        remove_str = Gtk.Label('REMOVE')

        remove_icon = Gtk.Image()
        remove_icon.set_from_file(image_dir + '/icons/remove.png')

        remove_contents = Gtk.Grid()
        remove_contents.set_row_spacing(0)
        remove_contents.set_column_spacing(0)
        remove_contents.attach(remove_icon, 0, 0, 1, 1)
        remove_contents.attach(remove_str, 1, 0, 1, 1)

        self.add(remove_contents)
        self.get_style_context().add_class('grey_linktext')
        self.set_alignment(1, 0.5)
