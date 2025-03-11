import network
import socket
import time
from machine import Pin, SoftI2C
from neopixel import NeoPixel
import dht
from ssd1306 import SSD1306_I2C

# NeoPixel RGB LED Setup
pin = Pin(48, Pin.OUT)  # Set GPIO48 to output for NeoPixel
neo = NeoPixel(pin, 1)  # Create NeoPixel driver on GPIO48 for 1 pixel

# DHT11 Sensor Setup
dht_pin = Pin(4)  # DHT11 Data pin (Change if needed)
sensor = dht.DHT11(dht_pin)

# OLED Display Setup
i2c = SoftI2C(scl=Pin(9), sda=Pin(8))  # Adjust based on wiring
oled = SSD1306_I2C(128, 64, i2c)

# Wi-Fi Configuration (STA Mode)
ssid = "NTU FSD"
#password = "12345676"
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(ssid)

# Wait for connection
while not sta.isconnected():
    time.sleep(1)

print("Connected to Wi-Fi! IP:", sta.ifconfig()[0])

# Access Point (AP) Mode
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32-AP", password="12345678")
print("AP Mode IP:", ap.ifconfig()[0])