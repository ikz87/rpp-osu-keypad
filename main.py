import usb_hid
import board
import time
import json
import supervisor
import os
from keys import Key
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

def main():
    # SETUP
    # Load configuration
    last_config_time = os.stat("config.json")[9]
    configs = ""
    with open("config.json", "r") as config_file:
        configs = json.load(config_file)
    general_configs = configs["general"]

    # HID keyboard
    kbd = Keyboard(usb_hid.devices)

    # Keys in the keypad
    keylist = [Key(id="key_1",
                        adc=board.GP28,
                        vcc=board.GP0)]

    # Config keys
    for key in keylist:
        # Set actions
        key_configs = configs[key.id]
        for i in range(len(key_configs)):
            key.actions.append(getattr(Keycode, key_configs[str(i)]))

        # Set everything else
        key.sensitivity = general_configs["sensitivity"]
        key.top_deadzone = general_configs["top_deadzone"]
        key.bottom_deadzone = general_configs["bottom_deadzone"]
        key.actuation_point = general_configs["actuation_point"]


    # TEMPORARY SOLUTION FOR ONE TIME CALIBRATION ON RELOAD
    for i in range(300):
        for key in keylist:
            key.poll()
            key.calibrate()
            time.sleep(0.01)
            print("calibrating", i)

    # LOOP
    while True:
        # Check if config has changed, if so, reload
        if last_config_time != os.stat("config.json")[9]:
            supervisor.reload()
        for key in keylist:
                key.poll()
                if general_configs["rapid_trigger"]:
                    key.rapid_trigger()
                else:
                    key.fixed_actuation()
                if key.curr_state:
                    if key.state_changed:
                        # Handle the keypress
                        # If action is a macro, just 
                        # send it once
                        if len(key.actions) > 1:
                            for keycode in key.actions:
                                kbd.send(keycode)
                        # If action is a single keycode
                        # press and hold
                        else:
                            kbd.press(key.actions[0])
                        pass
                else:
                    if key.state_changed:
                        kbd.release(key.actions[0])
                        pass
        pass
if __name__ == "__main__":
    main()
