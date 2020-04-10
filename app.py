import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def value_up(builder, name):
    widget = builder.get_object(name)
    widget.do_value_changed(Gtk.ScrollType.STEP_UP)


def value_down(builder, name):
    widget = builder.get_object(name)
    widget.do_value_changed(Gtk.ScrollType.STEP_DOWN)


def start_clicked(widget):
    label = widget.get_label()
    if label == "Start":
        widget.set_label("Stop")
    else:
        widget.set_label("Start")


if __name__ == "__main__":
    builder = Gtk.Builder()
    builder.add_from_file("layout.glade")
    handlers = {"onDestroy": Gtk.main_quit, "onStartClick": start_clicked}
    builder.connect_signals(handlers)

    window = builder.get_object("main_window")
    window.show_all()
    window.set_size_request(1920, 1080)
    window.fullscreen()

    Gtk.main()
