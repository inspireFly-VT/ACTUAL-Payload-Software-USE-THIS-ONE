from time import sleep_us, sleep
from machine import Pin

pet_time = 10000
# default pin is 20
class Watchdog:
    def __init__(self, pin=20):
        self.dog_pin = Pin(pin, Pin.OUT)
        self.dog_pin.value(0)

    def pet(self):
        # Pull high
        self.dog_pin.value(1)
        sleep_us(pet_time)
        # Pull low
        self.dog_pin.value(0)

dog = Watchdog()
# # 
# while True:
# 
# 
#     
#     dog.pet()
# 
#     print("Dog Pet")
# 
#     sleep(0.01)
