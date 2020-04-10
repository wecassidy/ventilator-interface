import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import rotary


def make_listbox_rotator(listbox, clockwise):
    def rotate():
        listbox.do_move_cursor(
            Gtk.MovementStep.GTK_MOVEMENT_DISPLAY_LINES,
            1 if rotary.Direction.CW else -1,
        )

    return rotate


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

    listbox = builder.get_object("control_container")
    r = rotary.RotaryEncoder(
        14,
        4,
        make_listbox_rotator(listbox, rotary.Direction.CW),
        make_listbox_rotator(listbox, rotary.Direction.CCW),
    )

    Gtk.main()
