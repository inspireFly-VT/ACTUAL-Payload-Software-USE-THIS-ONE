# Code created by David Encarnacion
# Last Updated: 11/4/2024 10:14

import time
from ssd1351 import Display
from machine import Pin, SPI, reset
from Camera import *
from easy_comms_micro import Easy_comms
import os
import math

# If you're using an external library, ensure it is imported correctly
try:
    import sdcard  # This should be directly available in most MicroPython builds
except ImportError:
    from lib import sdcard  # In case it's in a custom directory

# inspireFly commands
commands = {
    b'\x10':    'noop',
    b'\x11': 'hreset',   # new
    b'\x12': 'shutdown',
    b'\x13':    'query',    # new
    #b'\x14': 'exec_cmd',   # not getting implemented
    b'\x15': 'joke_reply',
    b'\x16': 'send_SOH',
    b'\x31': 'take_pic',
    b'\x32': 'send_pic',
    b'\x34': 'receive_pic',
}


class PCB:
    def __init__(self):
        # Initialize GPIO3 as an output pin
        self.pin3 = Pin(12, Pin.OUT)
        # Set GPIO3 to low
        self.pin3.value(0)
        self.spi_display = SPI(0, baudrate=14500000, sck=Pin(18), mosi=Pin(19))
        self.display = Display(self.spi_display, dc=Pin(14), cs=Pin(21), rst=Pin(7))
        
        # Initialize the camera if needed
        self.spi_camera = SPI(1, sck=Pin(10), miso=Pin(8), mosi=Pin(11), baudrate=8000000)
        self.cs = Pin(9, Pin.OUT)
        self.onboard_LED = Pin(25, Pin.OUT)
        self.cam = Camera(self.spi_camera, self.cs)

        # Initialize SD card (using SPI pins)
        sd = sdcard.SDCard(SPI(0), Pin(17))  # Adjust SPI and CS pins if needed
        os.mount(sd, '/sd')
        print("SD card mounted")

        # Communication setup
        self.com1 = Easy_comms(uart_id=1, baud_rate=9600)
        
        self.last_num = self.get_last_num()

    def get_last_num(self):
        try:
            with open('/sd/last_num.txt', 'r') as f:
                return int(f.read())
        except OSError:
            return 1

    # Rest of the class methods go here...


    def TakePicture(self, imageName, resolution):
        timeout_duration = 5  # Specify the timeout duration in seconds
        start_time = time.time()  # Record the start time

        self.onboard_LED.on()
        finalImageName = f"/sd/{imageName}.jpg"  # Ensure image is saved on SD card
        self.cam.resolution = resolution
        time.sleep(0.5)

        # Try to capture the image and reset if it takes too long
        try:
            self.cam.capture_jpg()
        except Exception as e:
            print("Error during capture:", e)

        # Check if the capture took too long
        if time.time() - start_time > timeout_duration:
            print("Picture capture timed out, resetting...")

        time.sleep(0.5)
        self.cam.saveJPG(finalImageName)  # Save explicitly to SD card
        self.onboard_LED.off()

        # Update last number
        try:
            with open('/sd/last_num.txt', 'w') as f:
                f.write(str(self.last_num + 1))
        except OSError:
            print("Error: Unable to update last_num.txt on SD card.")


    def TakeMultiplePictures(self, imageName, resolution, interval, count):
        self.cam.resolution = resolution
        for x in range(count):
            endImageName = f"{imageName}{self.last_num}"
            self.TakePicture(endImageName, resolution)
            sleep_ms(500)
            if x == 0:
                try:
                    os.remove(f"{endImageName}.jpg")
                except OSError:
                    print(f"Error removing file: {endImageName}.jpg")
            sleep_ms(interval)

    def display_image(self, image_path):
        self.display.draw_image(image_path, 0, 0, 128, 128)

    def communicate_with_fcb(self, jpg_bytes):
        self.com1.overhead_send('ping')
        print("Ping sent...")
        while True:
            command = self.com1.overhead_read()
            if command.lower() == 'chunk':
                print('Sending communications acknowledgment...')
                self.com1.overhead_send('acknowledge')
                print('Acknowledgment sent, commencing data transfer...')
                time.sleep(2)
                self.send_chunks(jpg_bytes)
            elif command.lower() == 'end':
                print('See you space cowboy...')
                break

    def send_chunks(self, jpg_bytes):
        chunksize = 66
        message = self.com1.overhead_read()

        if message != "Wrong" and message != "No image data received":
            a, b = map(int, message.split())
            for i in range(a, b + 1):
                print("Chunk #", i)
                self.onboard_LED.off()
                chunk = jpg_bytes[i * chunksize:(i + 1) * chunksize]
                chunknum = i.to_bytes(2, 'little')
                chunk = chunknum + chunk
                
                crctagb = self.com1.calculate_crc16(chunk)
                chunk += crctagb.to_bytes(2, 'little')
                
                self.onboard_LED.on()
                self.com1.send_bytes(chunk)
                print(len(chunk))
                while (recievecheck := self.com1.overhead_read()) == "Chunk has an error.":
                    self.com1.send_bytes(chunk)
                self.onboard_LED.off()
                
            print("All requested chunks sent successfully.")
        elif message == "No image data received":
            print("No image data received by 'a' side. Ending chunk transfer process.")
            
    def wait_for_command(self):
        """Continuously check for a command from the FCB before proceeding."""
        while True:
            print("Checking for command from FCB...")
            command = self.com1.overhead_read()
            print(command)
            if command in commands:
                command_name = commands[command]
                print(f"Received command: {command_name}")

                if command_name == 'noop':
                    pass  # No operation, do nothing
                elif command_name == 'hreset':
                    print("Resetting hardware.")
                elif command_name == 'shutdown':
                    print("Shutting down.")
                elif command_name == 'query':
                    print("Processing query.")
                elif command_name == 'joke_reply':
                    print("Responding with a joke.")
                elif command_name == 'send_SOH':
                    print("Sending start of header.")
                elif command_name == 'take_pic':
                    print("Taking a picture.")
                    self.display_image('RaspberryPiWB128x128.raw')
                    count = (self.last_num + 2) - self.last_num
                    print("Initiating TakeMultiplePictures...")

                    self.TakeMultiplePictures('inspireFly_Capture_', '320x240', 1, count)
                    command = b'\x32'
                elif command_name == 'send_pic':
                    print("Sending picture.")
                    file_path = f"/sd/inspireFly_Capture_{self.last_num}.jpg"
                    try:
                        with open(file_path, "rb") as file:
                            jpg_bytes = file.read()
                        print("File found, initiating data transmission with flight computer...")
                        self.communicate_with_fcb(jpg_bytes)
                    except OSError:
                        print(f"Error: File {file_path} does not exist. Cannot send picture.")
                elif command_name == 'receive_pic':
                    print("Receiving picture.")
            else:
                print(f"Unknown command received: {command}")

            time.sleep(0.5)  # Adjust polling interval as needed

