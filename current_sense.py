from machine import ADC
import time

# Initialize ADC on pin 26 (GP26 corresponds to ADC0)


def get_average_current(device):

    adc_display = ADC(26)
    adc_camera = ADC(27)
    VREF = 3.3
    sample_size = 50
    
    if device == "camera":
        device = adc_camera
    elif device == "display":
        device = adc_display
    else:
        return "Incorect name: 'display' or 'camera'"
    
    raw_value = 0
    for i in range(sample_size):
        raw_value += device.read_u16()
        time.sleep(0.01)
    
    # Convert the raw value to a voltage
    voltage = (raw_value / 65535) * VREF /sample_size  # 16-bit ADC scale (0-65535)
    amperage = voltage / (0.065 * 100)
    
    # Print the voltage
    print("Voltage: {:.2f} V".format(voltage))
    print("Amperage: {:.2f} A".format(amperage))
    
    return amperage
    

