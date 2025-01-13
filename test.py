from machine import Pin, ADC            #importing Pin and ADC class
from time import sleep                  #importing sleep class

display = ADC(26)            #creating potentiometer object
camera = ADC(27)
reset = Pin(12, Pin.OUT)

reset.on()

reset.off()


while True:
    display_value = 0
    camera_value = 0
    for i in range(10000):
         display_value += display.read_u16() * 3.3 / 65536  #reading analog pin
         camera_value += camera.read_u16() * 3.3 / 65536  #reading analog pin

    print("display",display_value/10000)                   #printing the ADC value
    print("camera",camera_value/10000)                   #printing the ADC value
    print("")
    sleep(0.25)
 
