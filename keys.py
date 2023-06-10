import analogio
import usb_hid
import board
import math
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

class key():
    def __init__(self, id, pin, keycode):
        # Set up pin and id
        self.id = id
        self.pin = analogio.AnalogIn(pin)
        self.keycode = keycode


        # Used for calibration
        self.top_adc = 0
        self.top_dist = 0
        self.bot_adc = 100000
        self.bot_dist = 100000
        self.travel_dist = 4

        # Value that's updated for key presses
        self.curr_adc = 0 # ADC
        self.curr_dist = 0 # Distance

        # For rapid trigger
        self.sens = 0.3
        self.hook = 0
        self.top_deadzone = 0.3
        self.bot_deadzone = 1.0

        # For fixed actuation
        self.actuation_point = 1.5

        # State of the switch
        self.curr_state = False
        self.state_changed = False


    def poll(self):
        # Poll 200 times and average values
        # This will make noise go away (kinda)
        avgrange = 200
        avg = 0
        for _i in range(avgrange):
            avg += self.pin.value
        avg = avg/avgrange
        self.curr_adc = avg
        pass


    def adc_to_dist(self, adc):
        """
        Gets distance in mm from an adc value
        """
        # Normalize
        dist = (adc - self.bot_adc)/(self.top_adc - self.bot_adc)

        # Make the function linear
        dist = math.sqrt(dist)

        # Scale to travel distance 
        dist *= self.travel_dist
        return dist


    def calibrate(self):
        # Calibrate values
        if self.curr_adc > self.top_adc:
            self.top_adc = self.curr_adc
        elif self.curr_adc < self.bot_adc:
            self.bot_adc = self.curr_adc
        self.top_dist = self.adc_to_dist(self.top_adc)
        self.bot_dist = self.adc_to_dist(self.bot_adc)
        #print(bot_dist, top_dist)
        pass


    def rapid_trigger(self):
        self.curr_dist = self.adc_to_dist(self.curr_adc)
        new_state = self.curr_state

        # Implement rapid trigger
        if self.curr_dist >=self.hook + self.sens:
            self.hook = self.curr_dist
            new_state = True
        elif self.curr_dist <=self.hook - self.sens:
            new_state = False
            self.hook = self.curr_dist

        # Keep hook in a safe range
        if self.hook < self.bot_dist + self.bot_deadzone:
            self.hook = self.bot_dist + self.bot_deadzone
        elif self.hook > self.top_dist - self.top_deadzone:
            self.hook = self.bot_dist - self.top_deadzone

        # Keep track of wether the state of the key has changed
        if new_state != self.curr_state:
            self.curr_state = new_state
            self.state_changed = True
        else:
            self.state_changed = False


    def fixed_actuation(self):
        new_state = self.curr_state
        self.curr_dist = self.adc_to_dist(self.curr_adc)

        if self.curr_dist >=self.actuation_point:
            new_state = True
        else:
            new_state = False

        # Keep track of wether the state of the key has changed
        if new_state != self.curr_state:
            self.curr_state = new_state
            self.state_changed = True
        else:
            self.state_changed = False
        pass
