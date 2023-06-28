import json
import time
import board
import analogio
import keys
import supervisor
from digitalio import DigitalInOut, Direction, Pull


def calibrate():
    """
    Calibrate every key in the keys.key_list
    """
    # Set up button
    calibration_button = DigitalInOut(board.GP14)
    calibration_button.direction = Direction.INPUT
    calibration_button.pull = Pull.DOWN

    # Calibrate keys while button is held
    while calibration_button.value:
        for key in keys.key_list:
            key.poll()
            key.calibrate()

    # Log values
    calibration_dict = {}
    for key in keys.key_list:
        calibration_dict[key.id] = {}
        calibration_dict[key.id]["top_adc"] = key.top_adc
        calibration_dict[key.id]["bottom_adc"] = key.bottom_adc
    print(calibration_dict)
    with open("calibration_values.json", "w") as calibration_file:
        json.dump(calibration_dict, calibration_file)

    # Start main once calibration is over
    supervisor.set_next_code_file("main.py")
    supervisor.reload()


if __name__ == "__main__":
    calibrate()
