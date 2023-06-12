import analogio
import usb_hid
import board
import math
from digitalio import DigitalInOut, Direction, Pull
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

class Key():
    def __init__(self, id, adc, vcc, keycode):
        # Set up pins and id
        self.id = id
        self.adc = analogio.AnalogIn(adc)
        self.vcc = DigitalInOut(vcc)
        self.vcc.direction = Direction.OUTPUT
        self.keycode = keycode

        # Used for calibration
        self.bot_adc = 0
        self.top_adc = 100000
        self.travel_dist = 4

        # Value that's updated for key presses
        self.curr_adc = 0
        self.curr_dist = 0

        # For rapid trigger
        self.sens = 0.3
        self.hook = 0
        self.top_deadzone = 1
        self.bot_deadzone = 0.3

        # For fixed actuation
        self.actuation_point = 1.5

        # State of the switch
        self.curr_state = False
        self.state_changed = False


    def poll(self):
        """
        Poll 200 times and average values
        """
        # Turn on vcc for polling
        self.vcc.value = True

        avgrange = 200
        avg = 0
        for _i in range(avgrange):
            avg += self.adc.value

        # Turn off vcc after polling
        self.vcc.value = False

        avg = avg/avgrange
        self.curr_adc = avg
        pass


    def adc_to_dist(self, adc):
        """
        Gets distance in mm from an adc value
        """
        # Normalize
        dist = (adc + 0.1 - self.top_adc)/(self.bot_adc - self.top_adc)

        # Make the function linear
        try:
            dist = math.sqrt(dist)
            #dist = math.sqrt(-((-dist+1)**2)+1)
        except:
            pass

        # Scale to travel distance 
        dist = dist * self.travel_dist - 0.1
        return dist


    def calibrate(self):
        """
        Calibrate key. Meant to be used repeatedly
        """
        # Calibrate values
        if self.curr_adc > self.bot_adc:
            self.bot_adc = (self.bot_adc + self.curr_adc)/2
        elif self.curr_adc < self.top_adc:
            self.top_adc = (self.top_adc + self.curr_adc)/2

        # Failsafe
        if self.top_adc == self.bot_adc:
            self.bot_adc += 0.1
        #print(self.top_adc, self.bot_adc, self.curr_adc)
        pass


    def rapid_trigger(self):
        """
        Wooting's rapid trigger technology
        """
        self.curr_dist = self.adc_to_dist(self.curr_adc)

        # Keep current distance and hook in a safe range
        if self.curr_dist > self.travel_dist - self.bot_deadzone:
            self.curr_dist = self.travel_dist
            self.hook = self.travel_dist - self.bot_deadzone
            self.update_state(True)
            return
        elif self.curr_dist < self.top_deadzone:
            self.curr_dist = 0
            self.hook = self.top_deadzone
            self.update_state(False)
            return

        # Implement rapid trigger
        if self.curr_dist >=self.hook + self.sens:
            self.hook = self.curr_dist
            self.update_state(True)
            return
        elif self.curr_dist <=self.hook - self.sens:
            self.hook = self.curr_dist
            self.update_state(False)
            return
        self.update_state(self.curr_state)


    def fixed_actuation(self):
        """
        Standard keyboard implementation
        """
        self.curr_dist = self.adc_to_dist(self.curr_adc)

        if self.curr_dist >=self.actuation_point:
            self.update_state(True)
        else:
            self.update_state(False)
        pass


    def update_state(self, state):
        """
        Updates key state and keeps track of whether the
        state of the key has changed or not
        """
        if state != self.curr_state:
            self.curr_state = state
            self.state_changed = True
        else:
            self.state_changed = False
