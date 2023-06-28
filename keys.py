import analogio
import board
from digitalio import DigitalInOut, Direction, Pull


class Key():
    def __init__(self, id, adc, vcc):
        # Set up pins, id and evualuation method
        self.rapid_trigger = True
        self.id = id
        self.adc = adc
        self.vcc = DigitalInOut(vcc)
        self.vcc.direction = Direction.OUTPUT
        self.actions = []

        # Used for calibration
        self.bottom_adc = 0
        self.top_adc = 100000
        self.travel_dist = 4

        # Value that's updated for key presses
        self.curr_adc = 0
        self.curr_dist = 0

        # For rapid trigger
        self.sensitivity = 0.3
        self.top_deadzone = 1
        self.bottom_deadzone = 0.3
        self.hook = self.travel_dist - self.bottom_deadzone

        # For fixed actuation
        self.actuation_point = 1.5
        self.actuation_reset = 0.3

        # State of the switch
        self.curr_state = False
        self.state_changed = False


    def poll(self):
        """
        Poll 20 times and average values
        """
        # Turn on vcc for polling
        self.vcc.value = True

        avgrange = 20
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
        dist = (adc - self.top_adc)/(self.bottom_adc - self.top_adc)

        # Make the function linear
        try:
            # 100% this doesn't work lmao, but it makes it better
            # dist = math.sqrt(dist)
            # Nvm, turns out it was already linear? idk anymore
            pass
        except:
            pass

        # Scale to travel distance 
        dist = dist * self.travel_dist

        # Clamp for nicer values
        dist = max(min(self.travel_dist,dist),0)
        return dist


    def calibrate(self):
        """
        Calibrate key. Meant to be used repeatedly
        """
        # Calibrate values
        if self.curr_adc > self.bottom_adc:
            self.bottom_adc = (self.bottom_adc + self.curr_adc)/2
        elif self.curr_adc < self.top_adc:
            self.top_adc = (self.top_adc + self.curr_adc)/2

        # Failsafe
        if self.top_adc == self.bottom_adc:
            self.bottom_adc += 0.1
        pass


    def evaluate_rapid_trigger(self):
        """
        Wooting's rapid trigger technology
        """
        self.curr_dist = self.adc_to_dist(self.curr_adc)

        # Keep current distance and hook in a safe range
        if self.curr_dist > self.travel_dist - self.bottom_deadzone:
            #self.curr_dist = self.travel_dist
            self.hook = self.travel_dist - self.bottom_deadzone
            self.update_state(True)
            return
        elif self.curr_dist < self.top_deadzone:
            #self.curr_dist = 0
            self.hook = self.top_deadzone
            self.update_state(False)
            return

        # Implement rapid trigger
        if self.curr_dist >=self.hook + self.sensitivity:
            self.hook = self.curr_dist
            self.update_state(True)
            return
        elif self.curr_dist <=self.hook - self.sensitivity:
            self.hook = self.curr_dist
            self.update_state(False)
            return
        self.update_state(self.curr_state)


    def evaluate_fixed_actuation(self):
        """
        Standard keyboard implementation
        """
        self.curr_dist = self.adc_to_dist(self.curr_adc)

        if self.curr_dist >=self.actuation_point:
            self.update_state(True)
            #self.curr_dist = self.travel_dist
            return
        elif self.curr_dist < self.actuation_point - self.actuation_reset:
            self.update_state(False)
            #self.curr_dist = 0
            return
        self.update_state(self.curr_state)
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


# Keys in the keypad
key_adc = analogio.AnalogIn(board.GP28)
key_list = [Key(id="key_1",
                adc=key_adc,
                vcc=board.GP0),
            Key(id="key_2",
                adc=key_adc,
                vcc=board.GP1),
            Key(id="key_3",
                adc=key_adc,
                vcc=board.GP2),
            Key(id="key_4",
                adc=key_adc,
                vcc=board.GP3),
            Key(id="key_5",
                adc=key_adc,
                vcc=board.GP4),
            Key(id="key_6",
                adc=key_adc,
                vcc=board.GP5),
            Key(id="key_7",
                adc=key_adc,
                vcc=board.GP6),
            Key(id="key_8",
                adc=key_adc,
                vcc=board.GP7),
            Key(id="key_9",
                adc=key_adc,
                vcc=board.GP8)]
