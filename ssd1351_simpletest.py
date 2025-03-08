import machine
import time
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_ssd1351 import SSD1351

# Initialize SPI for MicroPython
spi = machine.SPI(1, baudrate=16000000, polarity=0, phase=0)
tft_cs = machine.Pin(5)   # Chip Select
tft_dc = machine.Pin(6)   # Data/Command
tft_rst = machine.Pin(9)  # Reset

# Initialize display bus
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)

# Initialize display
display = SSD1351(display_bus, width=128, height=128)

# Create display group
splash = displayio.Group()
display.show(splash)

# Background color (Green)
color_bitmap = displayio.Bitmap(128, 128, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00FF00  # Bright Green

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Inner rectangle (Purple)
inner_bitmap = displayio.Bitmap(108, 108, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0xAA0088  # Purple

inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=10, y=10)
splash.append(inner_sprite)

# Text label
text = "Hello World!"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=30, y=64)
splash.append(text_area)

# Keep display running
while True:
    time.sleep(1)
