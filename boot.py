import supervisor
import storage
import board
import usb_cdc
from digitalio import DigitalInOut, Direction, Pull

# Enable a data serial port
usb_cdc.enable(data=True)

# Disable autoreloading jic
supervisor.runtime.autoreload = False

# Change volume name
new_name = "KZOOTING"
storage.remount("/", readonly=False)
m = storage.getmount("/")
m.label = new_name

# Calibration mode
calibration_button = DigitalInOut(board.GP15)
calibration_button.direction = Direction.INPUT
calibration_button.pull = Pull.DOWN

if calibration_button.value:
    storage.remount("/", readonly=False)
    #supervisor.set_next_code_file("calibration.py")
else:
    storage.remount("/", readonly=True)
