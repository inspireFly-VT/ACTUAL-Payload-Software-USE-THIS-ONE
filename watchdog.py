from time import sleep_us
from machine import Pin

kick_time = 1
# default pin is 20
class Watchdog:
    def __init__(self, pin=20):
        self.dog_pin = pin
        self.dog_pin.off()

    def kick(self):
        # Pull high
        self.dog_pin.on()
        sleep_us(kick_time)
        # Pull low
        self.dog_pin.off()
