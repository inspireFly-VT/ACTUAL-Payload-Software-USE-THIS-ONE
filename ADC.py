from machine import ADC
import time

# Initialize ADC on pin 26 (GP26 corresponds to ADC0)
adc = ADC(26)

# Reference voltage (3.3V for the RP2040)
VREF = 3.3

while True:
    # Read the raw ADC value (0-4095)
    raw_value = 0
    for i in range(100):
        raw_value += adc.read_u16()
        time.sleep(0.01)
    
    # Convert the raw value to a voltage
    voltage = (raw_value / 65535) * VREF /100 * 2 # 16-bit ADC scale (0-65535)
    
    # Print the voltage
    print("Voltage: {:.2f} V".format(voltage))
