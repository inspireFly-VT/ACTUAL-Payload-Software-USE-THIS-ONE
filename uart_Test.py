import machine
import utime

# Configure UART (UART1 on GPIO4 as TX and GPIO5 as RX)
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

def test_uart():
    print("UART Test Started")
    
    # Send test message
    message = "Hello, UART!\n"
    uart.write(message)
    print(f"Sent: {message.strip()}")

    utime.sleep(1)  # Give some time for the data to be received

    # Check for incoming data
    if uart.any():
        received_data = uart.read().decode('utf-8')
        print(f"Received: {received_data.strip()}")

while True:
    test_uart()
    utime.sleep(2)
