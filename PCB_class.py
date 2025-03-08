import time
import os
import math
from machine import Pin, SPI, reset
from ssd1351 import Display
from Camera import Camera
from easy_comms_micro import Easy_comms
from watchdog import Watchdog

# Try to import sdcard, fallback if in a custom directory
try:
    import sdcard
except ImportError:
    from lib import sdcard
    
# inspireFly commands
#Fix commands for how they are sent over by the FCB
commands = {
    b'\x10'	:    'noop',		# no operation
    b'\x11'	: 'hreset',   		# hardware reset (new)
    b'\x12'	: 'shutdown',		# shutdown payload
    b'\x13'	:    'query',    	# new
    #b'\x14': 'exec_cmd',   	# not getting implemented
    b'\x15'	: 'joke_reply',		# joke reply
    b'\x16'	: 'send_SOH',		#send state of health
    '1' 	: 'take_pic',		#take a pic
    '2'	: 'send_pic',		#send a pic
    b'\x34'	: 'receive_pic'		#receive a pic
}

dog = Watchdog()

class PCB:
    def __init__(self):
        dog.pet()
        self.cam_Pin = Pin(12, Pin.OUT, value=0)
        self.spi_display = SPI(0, baudrate=14500000, sck=Pin(18), mosi=Pin(19))
        self.display = Display(self.spi_display, dc=Pin(14), cs=Pin(21), rst=Pin(22))
        
        self.spi_camera = SPI(1, sck=Pin(10), miso=Pin(8), mosi=Pin(11), baudrate=8000000)
        self.cs = Pin(9, Pin.OUT)
        self.onboard_LED = Pin(25, Pin.OUT)
        self.cam = Camera(self.spi_camera, self.cs)
        
        sd = sdcard.SDCard(SPI(0), Pin(17))  
        os.mount(sd, '/sd')
        print("SD card mounted")
        
        self.com1 = Easy_comms(uart_id=0, baud_rate=9600)
        self.last_num = self.get_last_num()
        self.cam_Pin(0)


    def get_last_num(self):
        try:
            with open('/sd/last_num.txt', 'r') as f:
                return int(f.read())
        except OSError:
            return 1

    def TakePicture(self, imageName, resolution):
        timeout_duration = 5  
        start_time = time.time()
        
        self.onboard_LED.on()
        finalImageName = f"/sd/{imageName}.jpg"
        self.cam.resolution = resolution
        time.sleep(0.5)
        dog.pet()
        
        try:
            self.cam.capture_jpg()
        except Exception as e:
            print("Error during capture:", e)

        if time.time() - start_time > timeout_duration:
            print("Picture capture timed out, resetting...")
        
        time.sleep(0.5)
        self.cam.saveJPG(finalImageName)
        self.onboard_LED.off()
        dog.pet()

        try:
            with open('/sd/last_num.txt', 'w') as f:
                f.write(str(self.last_num + 1))
        except OSError:
            print("Error: Unable to update last_num.txt on SD card.")
    
    def TakeMultiplePictures(self, imageName, resolution, interval, count):
        time.sleep(1)
        self.cam_Pin(0)
        time.sleep(1)
        self.cam.resolution = resolution
        for x in range(count):
            endImageName = f"{imageName}{self.last_num}"
            self.TakePicture(endImageName, resolution)
            time.sleep(1)
            if x == 0:
                try:
                    os.remove(f"/sd/{endImageName}.jpg")
                except OSError:
                    print(f"Error removing file: {endImageName}.jpg")
            time.sleep(interval)
#         self.cam_Pin(1)
            
    def display_image(self, image_path):
        try:
            print(f"Attempting to display {image_path}")
            self.display.draw_image(image_path, 0, 0, 128, 128)
            print("Image displayed successfully")
        except Exception as e:
            print(f"Error displaying image: {e}")


    def communicate_with_fcb(self, jpg_bytes):
        self.com1.overhead_send('ping')
        print("Ping sent...")
        
        while True:
            command = self.com1.overhead_read()
            if command.lower() == 'chunk':
                print('Sending acknowledgment...')
                self.com1.overhead_send('acknowledge')
                print('Acknowledgment sent, commencing data transfer...')
#                 time.sleep(2)
                self.com1.wait_for_acknowledgment()
                time.sleep(2)
                self.send_chunks(jpg_bytes)
            elif command.lower() == 'end':
                print('Transmission complete.')
                break

    def send_chunks(self, jpg_bytes):
        chunksize = 66
        num_chunks = math.ceil(len(jpg_bytes) / chunksize)
        print(jpg_bytes)
        print(f"Number of Chunks: {num_chunks}")
        
        self.com1.overhead_send(str(num_chunks))
        print(f"Sent num_Chunks: {num_chunks}")
        time.sleep(2)
        
#         if self.com1.overhead_read() == "acknowledge":
        for i in range(num_chunks):
            print(f"Chunk #{i}")
            self.onboard_LED.off()
            
            chunk = jpg_bytes[i * chunksize:(i + 1) * chunksize]
            chunknum = i.to_bytes(2, 'little')
            chunk = chunknum + chunk
            chunk += self.com1.calculate_crc16(chunk).to_bytes(2, 'little')
            
            self.onboard_LED.on()
            self.com1.send_bytes(chunk)
            print(f"Sent chunk of length {len(chunk)} bytes")
            time.sleep(1.5)
            
            retries = 0
            retry_limit = 5
            while (receive_check := self.com1.overhead_read()) == "Chunk has an error." and retries < retry_limit:
                retries += 1
                self.com1.send_bytes(chunk)
                print(f"Retrying chunk {i}, attempt {retries}")
            
            self.onboard_LED.off()

        print("All requested chunks sent successfully.")

    def wait_for_command(self):
        index = 1  # Start the index for each state of health record
        while True:
            dog.pet()
            print("Checking for command from FCB...")
            command = self.com1.overhead_read()
            print(command)

            if command in commands:
                command_name = commands[command]
                print(f"Received command: {command_name}")

                if command_name == 'noop':
                    pass  
                elif command_name == 'hreset':
                    print("Resetting hardware.")
                    reset()
                elif command_name == 'shutdown':
                    print("Shutting down.")
                elif command_name == 'query':
                    print("Processing query.")
                elif command_name == 'send_SOH':
                    print("Sending State of Health")
                    import current_sense as amp
                    # Get current values for camera and display
                    display_current = amp.get_average_current("display")
                    camera_current = amp.get_average_current("camera")
                    
                    # Index the data instead of using a timestamp
                    # Format index like "Index: 1", "Index: 2", etc.
                    indexed_data = f"Index: {index} - Display Current: {display_current:.2f} A, Camera Current: {camera_current:.2f} A"
                    
                    # Print the data to the shell
                    print(f"Display current: {display_current:.2f} A")
                    print(f"Camera current: {camera_current:.2f} A")
                    
                    # Send the data over UART to FCB
                    self.com1.overhead_send(indexed_data.encode())  # Sending data over UART
                    
                    # Write data to housekeeping file with index
                    housekeeping_file_path = '/sd/housekeeping.txt'
                    try:
                        with open(housekeeping_file_path, 'a') as file:
                            # Append the indexed data to the file
                            file.write(f"{indexed_data}\n")
                            print(f"SOH data with index written to {housekeeping_file_path}")
                        
                        # Increment the index for the next entry
                        index += 1

                    except OSError as e:
                        print(f"Error writing to housekeeping file: {e}")
                            
                elif command_name == 'take_pic':
                    print("Displaying image...")
                    time.sleep(1)
                    self.display_image("RaspberryPiWB128x128.raw")
                    time.sleep(1)
                    count = (self.last_num + 2) - self.last_num
                    print("Taking a picture.")
                    self.TakePicture(f'inspireFly_Capture_{self.last_num}', '320x240')
                elif command_name == 'send_pic':
                    file_path = f"/sd/inspireFly_Capture_{self.last_num - 1}.jpg"
                    try:
                        with open(file_path, "rb") as file:
                            jpg_bytes = file.read()
                        self.communicate_with_fcb(jpg_bytes)
                    except OSError:
                        print(f"Error: File {file_path} does not exist. Cannot send picture.")
                elif command_name == 'receive_pic':
                    print("Receiving picture.")
            else:
                print(f"Unknown command received: {command}")

            time.sleep(0.5)

