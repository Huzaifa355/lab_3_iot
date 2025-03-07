import network
import time
import BlynkLib
import dht
from machine import Pin
import ssd1306
from machine import Pin, I2C

# ---- USER SETTINGS ----
WIFI_SSID = "Huzaifa"    
WIFI_PASS = "12345678"        
BLYNK_AUTH = "p17kdKvaFFK5kXxMnzGNtjPtXDrXP6Xq"

# ---- CONNECT TO WIFI ----
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("🔄 Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            pass
    print("✅ Connected to WiFi:", wlan.ifconfig())

connect_wifi()

# ---- INITIALIZE BLYNK ----
blynk = BlynkLib.Blynk(BLYNK_AUTH, server="blynk.cloud", port=80, insecure=True)

# ---- INITIALIZE DHT SENSOR ----
dht_sensor = dht.DHT11(Pin(4))  # GPIO15 is used for DHT sensor

i2c = I2C(0, scl=Pin(9), sda=Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
# Clear display
oled.fill(0)

# ---- SEND DATA TO BLYNK ----
def send_sensor_data():
    try:
        dht_sensor.measure()  # Read DHT sensor
        time.sleep(1)  # Wait to stabilize readings

        temp = dht_sensor.temperature()  # Get temperature in °C
        humid = dht_sensor.humidity()  # Get humidity in %

        # Print values in console
        print(f"🌡 Temp: {temp:.2f}°C | 💧 Humidity: {humid:.2f}%")
        oled.text(f"Temp: {temp} C",10,16)
        oled.text(f"Humidity: {humid} %",10,32)
        oled.show()

        # Send data to Blynk in Double format
        blynk.virtual_write(0, round(temp, 2))  # Send Temperature to V0
        blynk.virtual_write(1, round(humid, 2))  # Send Humidity to V1

    except OSError as e:
        print(f"⚠️ Sensor Error: {e}")

# ---- MAIN LOOP ----
while True:
    blynk.run()
    send_sensor_data()
    time.sleep(5)  # Send data every 5 seconds
