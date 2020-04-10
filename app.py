import sys

import gpiozero as g0
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

    def rotate(self, direction):
        if (
            direction == rotary.Direction.DOWN
            and self.index < len(self.box.get_children()) - 1
        ):
            self.index += 1
        elif direction == rotary.Direction.UP and self.index > 0:
            self.index -= 1
        self.select_index()


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


class AppState:
    def __init__(self, listbox, builder, propertySender, startClicker):
        self.box = listbox
        self.builder = builder
        self.rotator = ListboxRotator(self.box)
        self.inSpinner = False
        self.sender = propertySender
        self.starter = startClicker

    def on_click(self):
        if self.inSpinner:
            self.sender(self.get_active_control())
            self.inSpinner = False
        elif self.box.get_selected_row() == self.box.get_children()[-1]:
            self.starter(self.get_active_control())
        else:
            self.inSpinner = True

    def on_up(self):
        if self.inSpinner:
            spinner = self.get_active_control()
            spinner.spin(Gtk.SpinType.STEP_FORWARD, spinner.get_increments()[0])
        else:
            self.rotator.rotate(rotary.Direction.UP)

    def on_down(self):
        if self.inSpinner:
            spinner = self.get_active_control()
            spinner.spin(Gtk.SpinType.STEP_BACKWARD, spinner.get_increments()[0])
        else:
            self.rotator.rotate(rotary.Direction.DOWN)

    def get_active_control(self):
        if self.rotator.index == len(self.box.get_children()) - 1:
            return self.builder.get_object("start")
        elif self.rotator.index == len(self.box.get_children()) - 2:
            return self.builder.get_object("i/e")
        else:
            return self.box.get_selected_row().get_children()[0].get_children()[-1]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError("Must provide serial port as command line argument")

    # Connect to serial
    ser = serial.Serial(sys.argv[1], baudrate=115200)

    # Build GUI
    builder = Gtk.Builder()
    builder.add_from_file("layout.glade")
    handlers = {
        "onDestroy": Gtk.main_quit,
        "onStartClick": make_start_clicker(ser),
    }
    builder.connect_signals(handlers)

    window = builder.get_object("main_window")
    window.show_all()
    window.set_size_request(1920, 1080)
    window.fullscreen()

    # Connect GUI to rotary encoder
    listbox = builder.get_object("control_container")
    state = AppState(listbox, builder, make_property_sender(ser), make_start_clicker(ser))
    # r = rotary.RotaryEncoder(
    #     14,
    #     4,
    #     rotator.make_listbox_rotator(rotary.Direction.CW),
    #     rotator.make_listbox_rotator(rotary.Direction.CCW),
    # )
    up = g0.Button(14, bounce_time=0.05)
    up.when_pressed = state.on_up
    down = g0.Button(4, bounce_time=0.05)
    down.when_pressed = state.on_down
    click = g0.Button(2, bounce_time=0.05)
    click.when_pressed = state.on_click

    Gtk.main()
