import network
import time
import BlynkLib
import dht
from machine import Pin

# WiFi Credentials
WIFI_SSID = "Huzaifa"
WIFI_PASS = "12345678"

# Blynk Authentication Token
BLYNK_AUTH = "VgWGfm_O0PIp6JtJE5SzgNor2nfDtsQi"

# Connect to WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...", end="")
while not wifi.isconnected():
    time.sleep(1)
    print(".", end="")
print("\nWiFi connected!")

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# Initialize DHT11 Sensor on GPIO 4
dht_sensor = dht.DHT11(Pin(4))

# Function to Read and Send Data
def send_sensor_data():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()  # Get Temperature
        hum = dht_sensor.humidity()  # Get Humidity
        
        print(f"Temperature: {temp}°C, Humidity: {hum}%")
        
        # Send Data to Blynk
        blynk.virtual_write(0, temp)  # Send Temp to V0
        blynk.virtual_write(1, hum)   # Send Hum to V1
    except Exception as e:
        print("Error reading sensor:", e)

# Run Blynk Loop
while True:
    blynk.run()
    send_sensor_data()
    time.sleep(5)  # Send data every 5 seconds
