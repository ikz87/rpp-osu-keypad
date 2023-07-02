import supervisor
import storage
import board
import usb_cdc
import usb_hid
from digitalio import DigitalInOut, Direction, Pull

# Enable a data serial port
# Should change console to False
# if no more changes are to be made
usb_cdc.enable(console=True, data=True)

# Only enable keyboard
usb_hid.enable((usb_hid.Device.KEYBOARD), boot_device=1)

# Disable autoreloading jic
supervisor.runtime.autoreload = False

# Change volume name (in case it is gonna be mounted)
new_name = "KZOOTING"
storage.remount("/", readonly=False)
m = storage.getmount("/")
m.label = new_name
storage.remount("/", readonly=True)

# Calibration mode
calibration_button = DigitalInOut(board.GP15)
calibration_button.direction = Direction.INPUT
calibration_button.pull = Pull.DOWN

# Don't mount volume
#storage.disable_usb_drive()

if calibration_button.value:
    supervisor.set_next_code_file("calibration.py")
