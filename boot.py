import supervisor
import storage
import board
import usb_cdc
from digitalio import DigitalInOut, Direction, Pull

# Enable a data serial port
# could set console=False if
# no more changes are to be done
# to the code. 
usb_cdc.enable(data=True)

# Disable autoreloading jic
supervisor.runtime.autoreload = False

# Calibration mode
calibration_button = DigitalInOut(board.GP15)
calibration_button.direction = Direction.INPUT
calibration_button.pull = Pull.DOWN

# Don't mount volume
storage.disable_usb_drive()

if calibration_button.value:
    supervisor.set_next_code_file("calibration.py")
