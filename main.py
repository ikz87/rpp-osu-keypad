import usb_hid
import board
import time
import keys
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

def main():
    # SETUP
    kbd = Keyboard(usb_hid.devices)
    keylist = [keys.Key(id=0, adc=board.GP28, vcc=board.GP0, keycode=Keycode.S)]
 #              keys.Key(id=1, adc=board.GP27, keycode=Keycode.D)]

    # TEMPORARY SOLUTION FOR ONE TIME CALIBRATION
    for i in range(1000):
        for key in keylist:
            key.poll()
            key.calibrate()
            time.sleep(0.01)
            print("calibrating", i)

    # LOOP
    while True:
        for key in keylist:
                key.poll()
                key.rapid_trigger()
                if key.curr_state:
                    if key.state_changed:
                        kbd.press(key.keycode)
                        #print("Press")
                        pass
                else:
                    if key.state_changed:
                        kbd.release(key.keycode)
                        pass
        pass
if __name__ == "__main__":
    main()
