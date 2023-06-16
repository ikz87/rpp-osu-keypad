from keys import Key
import json
import time
import board
import analogio
from digitalio import DigitalInOut, Direction, Pull

def calibrate():
    """
    Calibrate every key in the key_list
    """
    # Set up button
    calibration_button = DigitalInOut(board.GP14)
    calibration_button.direction = Direction.INPUT
    calibration_button.pull = Pull.DOWN

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

    # Calibrate keys while button is held
    while calibration_button.value:
        for key in key_list:
            key.poll()
            key.calibrate()
            time.sleep(0.001)

    # Log values
    calibration_dict = {}
    for key in key_list:
        calibration_dict[key.id] = {}
        calibration_dict[key.id]["top_adc"] = key.top_adc
        calibration_dict[key.id]["bottom_adc"] = key.bottom_adc
    print(calibration_dict)
    with open("calibration_values.json", "w") as calibration_file:
        json.dump(calibration_dict, calibration_file)


if __name__ == "__main__":
    calibrate()
