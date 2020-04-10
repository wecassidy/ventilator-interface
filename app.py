import sys

import serial
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import rotary


class ListboxRotator:
    def __init__(self, listbox):
        self.box = listbox
        self.index = 0
        self.select_index()

    def select_index(self):
        self.box.unselect_all()
        self.box.select_row(self.box.get_row_at_index(self.index))

    def make_listbox_rotator(self, direction):
        def rotate():
            if (
                direction == rotary.Direction.CW
                and self.index < len(self.box.get_children()) - 1
            ):
                self.index += 1
            elif direction == rotary.Direction.CCW and self.index > 0:
                self.index -= 1
            self.select_index()

        return rotate


def make_start_clicker(ser):
    def start_clicked(widget):
        label = widget.get_label()
        if label == "Start":
            widget.set_label("Stop")
            ser.write(b"$START*\n")
        else:
            widget.set_label("Start")
            ser.write(b"$STOP*\n")

    return start_clicked


def make_property_sender(ser):
    def send_new_property(spinner):
        property = Gtk.Buildable.get_name(spinner).upper()
        if property == "RISE":
            value = spinner.get_value()
            ser.write(f"${property},{value:.1f}*\n".encode("utf-8"))
        else:
            value = spinner.get_value_as_int()
            ser.write(f"${property},{value}*\n".encode("utf-8"))

    return send_new_property


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Must provide serial port as command line argument")

    # Connect to serial
    ser = serial.Serial(sys.argv[1], baudrate=115200)

    # Build GUI
    builder = Gtk.Builder()
    builder.add_from_file("layout.glade")
    handlers = {
        "onDestroy": Gtk.main_quit,
        "onStartClick": make_start_clicker(ser),
        "propertyChanged": make_property_sender(ser),
    }
    builder.connect_signals(handlers)

    window = builder.get_object("main_window")
    window.show_all()
    window.set_size_request(1920, 1080)
    window.fullscreen()

    # Connect GUI to rotary encoder
    listbox = builder.get_object("control_container")
    rotator = ListboxRotator(listbox)
    r = rotary.RotaryEncoder(
        14,
        4,
        rotator.make_listbox_rotator(rotary.Direction.CW),
        rotator.make_listbox_rotator(rotary.Direction.CCW),
    )

    Gtk.main()
