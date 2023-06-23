import usb_hid
import board
import json
import supervisor
import os
import keys
from microcontroller import cpu
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


def main():
    # SETUP
    # HID keyboard
    kbd = Keyboard(usb_hid.devices)

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
    keys_info = {}
    for key in keys.key_list:
        # Prepare out dictionary
        keys_info[key.id] = {}

        # Set calibrations
        key_calibrations = calibrations[key.id]
        key.top_adc = key_calibrations["top_adc"]
        key.bottom_adc = key_calibrations["bottom_adc"]

        # Set actions
        key_configs = configs[key.id]
        key_actions = key_configs["actions"]
        for i in range(len(key_actions)):
            for j in range(len(key_actions[i])):
                key_actions[i][j] = getattr(Keycode, key_actions[i][j])
                #key.actions.append(getattr(Keycode, action))
        key.actions = key_actions

        # Set everything else
        key.sensitivity = general_configs["sensitivity"]
        key.top_deadzone = general_configs["top_deadzone"]
        key.bottom_deadzone = general_configs["bottom_deadzone"]
        key.actuation_point = general_configs["actuation_point"]

    # LOOP
    counter = 0
    while True:
        # Check if config has changed, if so, reload
        if last_config_time != os.stat("config.json")[9]:
            supervisor.reload()
        for key in keys.key_list:
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
            keys_info[key.id]["state"] = key.curr_state
            keys_info[key.id]["distance"] = key.curr_dist

        if counter % 5 == 0:
            keys_json = json.dumps(keys_info)
            print(keys_json)
        counter += 1


if __name__ == "__main__":
    main()
