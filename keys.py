import analogio
import usb_hid
import board
import math
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

class Key():
    def __init__(self, id, pin, keycode):
        # Set up pin and id
        self.id = id
        self.pin = analogio.AnalogIn(pin)
        self.keycode = keycode

        # Used for calibration
        self.bot_adc = 0
        self.top_adc = 100000
        self.travel_dist = 4

        # Value that's updated for key presses
        self.curr_adc = 0 # ADC
        self.curr_dist = 0 # Distance

        # For rapid trigger
        self.sens = 0.3
        self.hook = 0
        self.top_deadzone = 1
        self.bot_deadzone = 0.2

        # For fixed actuation
        self.actuation_point = 1.5

        # State of the switch
        self.curr_state = False
        self.state_changed = False


    def poll(self):
        """
        Poll 200 times and average values
        """
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
        dist = (adc - self.top_adc)/(self.bot_adc - self.top_adc)

        # Make the function linear
        try:
            dist = math.sqrt(dist)
            #dist = math.sqrt(-((-dist+1)**2)+1)
        except:
            pass

        # Scale to travel distance 
        dist *= self.travel_dist
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
        new_state = self.curr_state

        # Keep current distance in a safe range
        if self.curr_dist > self.travel_dist - self.bot_deadzone:
            self.curr_dist = self.travel_dist
        elif self.curr_dist < self.top_deadzone:
            self.curr_dist = 0


        # Implement rapid trigger
        if self.curr_dist >=self.hook + self.sens:
            self.hook = self.curr_dist
            new_state = True
        elif self.curr_dist <=self.hook - self.sens:
            new_state = False
            self.hook = self.curr_dist

        # Keep track of wether the state of the key has changed
        if new_state != self.curr_state:
            self.curr_state = new_state
            self.state_changed = True
        else:
            self.state_changed = False


    def fixed_actuation(self):
        """
        Standard keyboard implementation
        """
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
