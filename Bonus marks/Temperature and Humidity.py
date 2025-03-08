import network
import time
import BlynkLib
import dht
from machine import Pin, I2C
import ssd1306

# ---- CONFIGURATION ----
WIFI_DETAILS = {"SSID": "Huzaifa", "PASSWORD": "12345678"}
BLYNK_TOKEN = "p17kdKvaFFK5kXxMnzGNtjPtXDrXP6Xq"

# ---- CONNECT TO WIFI ----
def establish_connection():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("🔄 Connecting to WiFi...")
        wlan.connect(WIFI_DETAILS["SSID"], WIFI_DETAILS["PASSWORD"])
        while not wlan.isconnected():
            pass
    print("✅ Connected! IP Address:", wlan.ifconfig()[0])

establish_connection()

# ---- INITIALIZING BLYNK ----
blynk = BlynkLib.Blynk(BLYNK_TOKEN, server="blynk.cloud", port=80, insecure=True)

# ---- SENSOR & DISPLAY SETUP ----
dht_sensor = dht.DHT11(Pin(4))  # DHT11 sensor on GPIO4
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)

def update_sensor_data():
    try:
        dht_sensor.measure()
        time.sleep(1)  # Allow sensor to stabilize
        
        temp = dht_sensor.temperature()
        humid = dht_sensor.humidity()

        # Display values on OLED
        oled.fill(0)
        oled.text(f"Temp: {temp} C", 10, 16)
        oled.text(f"Humidity: {humid} %", 10, 32)
        oled.show()

        # Send data to Blynk
        print(f"🌡 Temp: {temp:.2f}°C | 💧 Humidity: {humid:.2f}%")
        blynk.virtual_write(0, round(temp, 2))  # Temperature -> V0
        blynk.virtual_write(1, round(humid, 2))  # Humidity -> V1

    except OSError as error:
        print(f"⚠️ Sensor Error: {error}")

# ---- MAIN LOOP ----
while True:
    blynk.run()
    update_sensor_data()
    time.sleep(5)  # Update every 5 seconds
