#!/usr/bin/python3

import socket

HOST = '2.0.0.2'
PORT = 6454
HEADER = b'Art-Net' + bytearray((00, # Protocol Name
    00, 80, # Opcode
    00, 14, # Protocol Version
    00,     # Sequence
    00,     # Physical
    00, 00, # Universe
    00, 80))# Payload length (5 Panels with 16 channels)

# panel: 0-4
# position: 0-4
# color: {0: red, 1: green, 2:blue}
def get_led_number(panel, position, colorid):
    if panel < 0 or panel > 4:
        raise ValueError("There are only 5 panels. Pick from 0 to 4. Not {0}".format(panel))
    if position < 0 or position > 4:
        raise ValueError("There are only 5 positions in a panel. Pick from 0 to 4. Not {0}".format(position))
    if colorid < 0 or colorid > 2:
        raise ValueError("Only 0 for red, 1 for green and 2 for blue are valid color ids. Not {0}".format(colorid))
    return int(panel)*16+int(position)*3+int(colorid)+1


class Color(object):
    # Takes a string '#rrggbb' or a iterable of 3 integers
    def __init__(self, values = None):
        if values is not None:
            if type(values) == str:
                self.parse_string(values)
            else:
                self.values = list(values)
        else:
            self.values = [0,0,0]

    def parse_string(self, string):
        if string[0] == "#":
            split = (string[1:3], string[3:5], string[5:7])
            self.values = [int(x, 16) for x in split]
        else:
            raise ValueError("Unkown color format '{0}'".format(string))

# LED Controller for the troll cave.
# Color parameters take a string (currently only "#rrggbb" format), tuple of 3 integers in [0,255] or Color objects.

class LEDControl(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((HOST, PORT))
        self.state = [255 for i in range(80)]
   
    # Call this method or nothing will happen!! 
    def send(self):
        package = HEADER+bytearray(self.state)
        self.socket.send(package)

    def set_intensity(self, panel, position, colorid, value):
        if value < 0 or value > 255:
            raise ValueError('Color Value has to be in [0,255]. Not {0}'.format(value))
        self.state[get_led_number(panel, position, colorid)] = int(value)

    def get_intensity(self, panel, position, colorid):
        return self.state[get_led_number(panel, position, colorid)]

    # Set color auf LED Tripel at specified position.
    def set_color(self, panel, position, color):
        if type(color) != Color:
            color = Color(color)
        for colorid, value in enumerate(color.values):
            self.set_intensity(panel, position, colorid, value)
    
    # Set color auf LED Tripel at specified position on every panel.
    def set_position(self, position, color):
        for panel in range(5):
            self.set_color(panel, position, color)

    # Set color auf LED Tripel at all positions on one panel.
    def set_panel(self, panel, color):
        for position in range(5):
            self.set_color(panel, position, color)

    # Set color auf LED Tripel everywhere.
    def set_all(self, color):
        for panel in range(5): 
            self.set_panel(panel, color)

    def set_gnome(self, intensity):
         self.state[64] = intensity


class LEDUtils(LEDControl):
    def all_on(self):
        self.set_all('#ffffff')
        self.send()
    
    def all_off(self):
        self.set_all('#000000')
        self.send()

# test:
if __name__ == "__main__":
    utils = LEDUtils()
    utils.all_on()
