import usb_hid
import time
import board
from digitalio import DigitalInOut, Direction, Pull

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

def main():
    # SETUP
    kbd = Keyboard(usb_hid.devices)
    switch = DigitalInOut(board.GP0)
    switch.direction = Direction.INPUT
    switch.pull = Pull.DOWN

    # LOOP
    # Testing with a digital switch
    while True:
        if switch.value:
            kbd.press(Keycode.A)
        else:
            kbd.release(Keycode.A)
        # Release all keys.
        #kbd.release_all()
        pass


if __name__ == "__main__":
    main()
