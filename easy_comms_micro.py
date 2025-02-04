from machine import UART, Pin
from time import time_ns
from time import sleep

class Easy_comms:
    
    #Initialize
    uart_id = 0
    baud_rate = 9600
    timeout = 5*10^9#10000
    
    #Backend stuff 
    def __init__(self, uart_id: int, baud_rate: int = None):
        self.uart_id = uart_id
        if baud_rate: 
            self.baud_rate = baud_rate
        # Set the baud rate
        self.uart = UART(self.uart_id, self.baud_rate)
        # Initialise the UART serial port
        self.uart.init()            
    
    #Send bytes across
    def send_bytes(self, data: bytes):
        print("Sending bytes...")
        self.uart.write(data) #write data to port
    
    #Hello!
    def start(self):
        message = "Ahoy!\n"
        print(message)

    #CRC Bit Check, returns 2 bytes of integers
    def calculate_crc16(self, data: bytes) -> bytes:
        crc = 0x1D0F #CCITT-False is 0xFFFF,
        poly = 0x1021  # CRC-CCITT polynomial
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ poly
                else:
                    crc <<= 1
                crc &= 0xFFFF  # Limit to 16 bits
        return crc

    #Read bytes that has been sent across, strips the overhead and CRC also
    def read_bytes(self, lowerchunk, upperchunk)-> bytes:
        message = b""
        data = b""
        count = 0; #new
        chunksize = 70
        sleep(2) #wait for bytes to come in
        #Collect Chunks
        for i in range(int(lowerchunk), int(upperchunk)+1):
            sleep(1) #Wait a second for port to fill with bytes
            if (self.uart.any() > 0): #If the port has any bytes
                data = self.uart.read(chunksize) 
                print("Data", data)
            #CRC Check
            crctagbb = data[-2:] #Grab CRC from incoming chunk
            chunknum = data[:2] #Grab chunk number from incoming chunk
            print("Chunk number: ", chunknum)
            print("Crc tagbb: ",crctagbb)
            crctagb = int.from_bytes(crctagbb, 'little') #Convert CRC bytes to integer
            stripped_data = data[:-2] #Strip off CRC tag from original chunk
            crctaga = self.calculate_crc16(stripped_data) #Calculate stripped chunks' CRC tag
            stripped_data2 = stripped_data[2:] #This strips the overhead and leaves us with the photos bytes
            if crctaga == crctagb: #If CRC's equal each other, then the photo has no error!
                message = message + stripped_data2
                request = "A has recieved chunk with no error!"
                self.overhead_send(request) #Send this request to b confirming we are ready to recieve next chunk
                count = count + 1
            else:
                #If the chunk is corrupted:
                while crctaga != crctagb: 
                    request = "Chunk has an error."
                    print(request, i)
                    self.overhead_send(request)
                print("Successfully recieved chunk!")
            print("Chunk Byte length: ",len(message))
        if len(message) > 0:
           return message, count
        else:
            return None
    
    #This function is to send strings across the port
    def overhead_send(self, msg: bytes):
        print(f'Sending Message: {msg}...')
        msg = msg + '\n'
        self.uart.write(bytes(msg,'utf-8'))
    
    # This function is to read the strings that are sent across
    def overhead_read(self) -> str:
        new_line = False
        message = ""
        while not new_line:
            if self.uart.any() > 0:
                try:
                    raw_data = self.uart.read()
                    decoded_data = raw_data.decode('utf-8')  # Decode without 'errors' argument
                    print(f"Test: Decoded Data: {decoded_data}")
                    message += decoded_data
                except UnicodeError:
                    print("Unicode error encountered during decoding. Skipping invalid characters.")
                    # Optionally, you can manually filter out invalid characters here
                    continue  # Skip this iteration if there's a decoding issue
                
                if '\n' in message:
                    new_line = True
                    print(f"Test: {message}" + "testEnd")
                    message = message.strip('\n')
                    print(f"Test after strip: {message}" + "testEnd after strip")
                    
                    
                    return message
        return None

        
        
        
        