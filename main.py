import usb_hid
import board
from digitalio import DigitalInOut, Direction, Pull
import analogio
import keys
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

def main():
    # SETUP
    kbd = Keyboard(usb_hid.devices)
    keylist = [keys.key(id=1, pin=board.GP28, keycode=Keycode.S),
               keys.key(id=2, pin=board.GP27, keycode=Keycode.D)]
    # LOOP
    while True:
        for key in keylist:
            key.poll()
            key.calibrate()
            key.rapid_trigger()
            if key.curr_state:
                if key.state_changed:
                    kbd.press(key.keycode)
                    #print("Press")
                    pass
            else:
                if key.state_changed:
                    kbd.release(key.keycode)
                    #print("Release")
                    pass
            #key.fixed_actuation()

        pass
if __name__ == "__main__":
    main()
