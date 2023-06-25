import usb_hid
import board
import json
import keys
import usb_cdc
from microcontroller import cpu
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


def setup_keys(configs):
    """
    Sets up the keys in the key_list
    using values from a json
    """
    general_configs = configs["general"]

    # Config keys
    for key in keys.key_list:

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
        key.rapid_trigger = general_configs["rapid_trigger"]


def main():
    # SETUP
    # HID keyboard
    kbd = Keyboard(usb_hid.devices)

    # Serial in and out dictionary
    pico_info = {}

    # Load configs from file
    configs = ""
    with open("config.json", "r") as config_file:
        configs = json.load(config_file)

    setup_keys(configs)

    # Calibrate keys
    calibrations = ""
    with open("calibration_values.json", "r") as calibration_file:
        calibrations = json.load(calibration_file)

    for key in keys.key_list:
        # Set calibrations
        key_calibrations = calibrations[key.id]
        key.top_adc = key_calibrations["top_adc"]
        key.bottom_adc = key_calibrations["bottom_adc"]

        # Populate out dict
        pico_info[key.id] = {}

    # LOOP
    counter = 0
    while True:
        # Log temperature
        pico_info["temperature"] = cpu.temperature

        # Read from serial port if data is available
        if usb_cdc.data.in_waiting:
            in_data = usb_cdc.data.readline().decode()
            if in_data == "configs_request":
                out_data = json.dumps(configs)
                usb_cdc.data.write(out_data)
            else:
                # Set up keys again with the new info
                in_json = json.loads(in_data)
                setup_keys(in_json)

                # Write to configuration file
                with open("config.json", "w") as config_file:
                    json.dump(config_file, calibration_file)

        for key in keys.key_list:
            key.poll()
            if key.rapid_trigger:
                key.evaluate_rapid_trigger()
            else:
                key.evaluate_fixed_actuation()
            if key.curr_state:
                if key.state_changed:
                    # Handle the keypress
                    # If action is a macro, just 
                    # send it once
                    if len(key.actions) > 1:
                        for keycode in key.actions:
                            kbd.send(*keycode)
                    # If action is a single keycode list
                    # press and hold
                    else:
                        kbd.press(*key.actions[0])
                        pass
            else:
                if key.state_changed:
                    kbd.release(*key.actions[0])
                    pass
            pico_info[key.id]["state"] = key.curr_state
            pico_info[key.id]["distance"] = key.curr_dist

        if counter % 5 == 0:
            out_data = json.dumps(pico_info) + "\n"
            usb_cdc.data.write(out_data.encode())
        counter += 1


if __name__ == "__main__":
    main()
