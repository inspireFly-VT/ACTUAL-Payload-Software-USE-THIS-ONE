#Code created by David Encarnacion with assistance from ChatGPT
#Last Updated: 11/4/2024 10:14

from PCB_class import PCB
import time

pcb = PCB()

pcb.wait_for_command()

#     pcb.TakePicture('PicForLarsen10', '640x480')

# print("Displaying image...")
#The image displayed, for the purposes of the
#mission, must be modifyable to pull the latest
#image uploaded by the ground station
#TODO: Replace 'RaspberryPiWB128x128.raw' with a variable
#directory, pulled from the FCB memory
# while True:
# pcb.display_image('/sd/potato.raw')
# 
#     count = (pcb.last_num + 2) - pcb.last_num
#     print("Initiating TakeMultiplePictures...")
# 
#     pcb.TakeMultiplePictures('inspireFly_Capture_', '320x240', 1, count)
#     file_path = f"/sd/inspireFly_Capture_{pcb.last_num}.jpg"
#     with open(file_path, "rb") as file:
#         jpg_bytes = file.read()
# 
#     print("Initiating data transmission with flight computer...")
#     pcb.communicate_with_fcb(jpg_bytes)
