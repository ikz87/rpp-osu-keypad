import usb_hid
import analogio
import board
import json
import supervisor
import os
from keys import Key
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# HID keyboard
kbd = Keyboard(usb_hid.devices)

# Keys in the keypad
adc_list = [ analogio.AnalogIn(board.GP28) ]
key_list = [Key(id="key_1",
               adc=adc_list[0],
               vcc=board.GP0),
            Key(id="key_2",
               adc=adc_list[0],
               vcc=board.GP1),
            Key(id="key_3",
               adc=adc_list[0],
               vcc=board.GP2),
            Key(id="key_4",
               adc=adc_list[0],
               vcc=board.GP3),
            Key(id="key_5",
               adc=adc_list[0],
               vcc=board.GP4),
            Key(id="key_6",
               adc=adc_list[0],
               vcc=board.GP5),
            Key(id="key_7",
               adc=adc_list[0],
               vcc=board.GP6),
            Key(id="key_8",
               adc=adc_list[0],
               vcc=board.GP7),
            Key(id="key_9",
               adc=adc_list[0],
               vcc=board.GP8)]


def main():
    # SETUP
    # Load configurations
    last_config_time = os.stat("config.json")[9]
    configs = ""
    with open("config.json", "r") as config_file:
        configs = json.load(config_file)
    general_configs = configs["general"]

    # Load calibrations
    calibrations = ""
    with open("calibration_values.json", "r") as calibration_file:
        calibrations = json.load(calibration_file)

    # Config keys
    for key in key_list:
        # Set calibrations
        key_calibrations = calibrations[key.id]
        key.top_adc = key_calibrations["top_adc"]
        key.bottom_adc = key_calibrations["bottom_adc"]

        # Set actions
        key_configs = configs[key.id]
        total_actions = len(key_configs)
        for i in range(total_actions):
            action_keycodes = key_configs[str(i)].split(",")
            keycode_list = []
            for action_keycode in action_keycodes:
                keycode_list.append(getattr(Keycode, action_keycode))
            key.actions.append(keycode_list)

        # Set everything else
        key.sensitivity = general_configs["sensitivity"]
        key.top_deadzone = general_configs["top_deadzone"]
        key.bottom_deadzone = general_configs["bottom_deadzone"]
        key.actuation_point = general_configs["actuation_point"]

    # LOOP
    while True:
        # Check if config has changed, if so, reload
        if last_config_time != os.stat("config.json")[9]:
            supervisor.reload()
        for key in key_list:
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
                                kbd.send(*keycode)
                        # If action is a single keycode
                        # press and hold
                        else:
                            kbd.press(*key.actions[0])
                        pass
                else:
                    if key.state_changed:
                        kbd.release(*key.actions[0])
                        pass
        pass


if __name__ == "__main__":
    main()
