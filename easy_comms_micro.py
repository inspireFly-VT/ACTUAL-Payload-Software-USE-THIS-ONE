from machine import UART, Pin
from time import time
import time

class Easy_comms:
    # Initialize with UART configuration
    def __init__(self, uart_id: int, baud_rate: int = None):
        self.uart_id = uart_id
        if baud_rate: 
            self.baud_rate = baud_rate
        # Set the baud rate for UART
        self.uart = UART(self.uart_id, self.baud_rate)
        # Initialize the UART serial port
        self.uart.init() 
    
    # Send bytes across UART
    def send_bytes(self, data: bytes):
        print("Sending bytes...")
        self.uart.write(data)
    
    # Calculate CRC16 for data integrity
    def calculate_crc16(self, data: bytes) -> bytes:
        crc = 0x1D0F  # CCITT-False is 0xFFFF
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

    # Send string messages across UART
    def overhead_send(self, msg: bytes):
        print(f'Sending Message: {msg}...')
        msg = msg + '\n'
        self.uart.write(bytes(msg, 'utf-8'))
    
    # Read string messages from UART
    def overhead_read(self) -> str:
        new_line = False
        message = ""
        while not new_line:
            if self.uart.any() > 0:
                try:
                    raw_data = self.uart.read()
                    decoded_data = raw_data.decode('utf-8')  # Decode without 'errors' argument
                    print(f"Decoded Data: {decoded_data}")
                    message += decoded_data
                except UnicodeError:
                    print("Unicode error encountered. Skipping invalid characters.")
                    continue  # Skip this iteration if there's a decoding issue
                
                if '\n' in message:
                    new_line = True
                    print(f"Received message: {message.strip()}")
                    message = message.strip('\n')  # Remove the newline character
                    return message
        return None

    # Wait for acknowledgment from the FCB
    def wait_for_acknowledgment(self, timeout=30):
        """
        Waits for an acknowledgment from the FCB.
        If acknowledgment is received, it proceeds with the data transfer.
        If timeout is reached without receiving acknowledgment, it returns False.
        
        :param timeout: Time in seconds to wait before giving up (default is 30 seconds).
        :return: True if acknowledgment is received, False if timeout is reached.
        """
        start_time = time.time()
        
        while True:
            acknowledgment = self.overhead_read()
            
            if acknowledgment == 'acknowledge':
                print('Acknowledgment received, proceeding with data transfer...')
                return True
            
            if time.time() - start_time > timeout:
                print("Timeout reached. No acknowledgment received.")
                return False
            
            time.sleep(1)  # Wait for a while before trying again
