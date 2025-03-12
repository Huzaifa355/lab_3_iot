from machine import Pin, I2C
import network
import time
import dht
import ssd1306
import socket

# WiFi Credentials
SSID = "Dhanju"
PASSWORD = "Huzaifa3550"

# Initialize OLED Display
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize DHT11 Sensor
dht_pin = Pin(4)
dht_sensor = dht.DHT11(dht_pin)

# Function to Read Sensor Data
def read_sensor():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        return temp, hum
    except:
        return None, None