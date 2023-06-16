import supervisor
import storage
import board
from digitalio import DigitalInOut, Direction, Pull

# Disable autoreloading jic
supervisor.runtime.autoreload = False

# Calibration mode
calibration_button = DigitalInOut(board.GP15)
calibration_button.direction = Direction.INPUT
calibration_button.pull = Pull.DOWN

if calibration_button.value:
    storage.remount("/", readonly=False)
    supervisor.set_next_code_file("calibration.py")
