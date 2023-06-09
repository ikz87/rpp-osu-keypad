import usb_hid
import board
import json
import keys
import usb_cdc
import supervisor
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
            try:
                for j in range(len(key_actions[i])):
                    key_actions[i][j] = getattr(Keycode, key_actions[i][j])
                #key.actions.append(getattr(Keycode, action))
            except:
                pass
        key.actions = key_actions

        # Set everything else
        key.sensitivity = general_configs["sensitivity"]
        key.top_deadzone = general_configs["top_deadzone"]
        key.bottom_deadzone = general_configs["bottom_deadzone"]
        key.actuation_point = general_configs["actuation_point"]
        key.rapid_trigger = general_configs["rapid_trigger"]


counter = 0
def main():
    # SETUP
    # HID keyboard
    kbd = Keyboard(usb_hid.devices)

    # Serial in and out dictionary
    pico_info = {}
    pico_info["message_type"] = "info_request_response"

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

    # Prepare some info lists
    temperatures = []
    report_times = []
    smoothing_len = 20
    for _i in range(smoothing_len):
        temperatures.append(1)
        report_times.append(1)

    # LOOP
    counter = 0
    usb_cdc.data.flush()
    last_report = supervisor.ticks_ms()
    while True:
        # Get current report time
        report_times.append(supervisor.ticks_ms() - last_report)
        last_report = supervisor.ticks_ms()
        report_times.pop(0)

        # Get current temperature
        temperatures.append(cpu.temperature)
        temperatures.pop(0)

        # Average stuff
        report_times_avg = 0
        temperatures_avg = 0
        for i in range(smoothing_len):
            report_times_avg += report_times[i]
            temperatures_avg += temperatures[i]
        report_times_avg /= smoothing_len
        temperatures_avg /= smoothing_len

        # Log smooth stuff
        pico_info["temperature"] = temperatures_avg
        pico_info["report_time"] = report_times_avg

        for key in keys.key_list:
            key.poll(20)
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

        # Read from serial port if data is available
        if usb_cdc.data.in_waiting > 0 and usb_cdc.data.out_waiting == 0:
            in_data = usb_cdc.data.readline().decode()
            if in_data == "configs_request\n":
                out_dict = configs
                out_dict["message_type"] = "configs_request_response"
                out_data = json.dumps(out_dict) + "\n"
                usb_cdc.data.write(out_data.encode())

            elif in_data == "info_request\n":
                out_dict = pico_info
                out_data = json.dumps(out_dict) + "\n"
                usb_cdc.data.write(out_data.encode())

            else: # This is a new config json
                # Set up keys again with the new info
                configs = json.loads(in_data)
                setup_keys(configs)

                # Write to configuration file
                with open("config.json", "w") as config_file:
                    json.dump(configs, config_file)
        counter += 1
if __name__ == "__main__":
    main()
