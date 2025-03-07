import network
import time
import BlynkLib
import neopixel
import machine
import ssd1306
from machine import Pin, I2C

# ---- USER SETTINGS ----
WIFI_SSID = "Huzaifa"    
WIFI_PASS = "12345678"        
BLYNK_AUTH = "p17kdKvaFFK5kXxMnzGNtjPtXDrXP6Xq"    

NEOPIXEL_PIN = 48   # GPIO pin where NeoPixel is connected
NUM_PIXELS = 1      # Number of NeoPixels

# ---- CONNECT TO WIFI ----
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi:", WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(1)
    print("Connected to Wi-Fi! IP:", wlan.ifconfig()[0])

connect_wifi()

# ---- INITIALIZE BLYNK ----
blynk = BlynkLib.Blynk(BLYNK_AUTH, server="blynk.cloud", port=80, insecure=True)
@blynk.on("connected")
def blynk_connected():
    print("✅ Connected to Blynk!")

@blynk.on("disconnected")
def blynk_disconnected():
    print("❌ Disconnected from Blynk!")

# ---- INITIALIZE NEOPIXEL ----
np = neopixel.NeoPixel(machine.Pin(NEOPIXEL_PIN), NUM_PIXELS)

# ---- SET NEOPIXEL COLOR ----
def set_color(r, g, b):
    np[0] = (r, g, b)
    np.write()
    print(f"NeoPixel Color: R={r}, G={g}, B={b}")

# ---- CORRECTED HUE TO RGB CONVERSION ----
def hsv_to_rgb(h):
    """ Convert HSV (hue,100,100) to RGB (0-255) """
    h = h / 255.0 * 360  # Convert to 0-360 range
    X = (1 - abs((h / 60) % 2 - 1)) * 255  # Calculate X for RGB formula

    if 0 <= h < 60:
        r, g, b = 255, X, 0
    elif 60 <= h < 120:
        r, g, b = X, 255, 0
    elif 120 <= h < 180:
        r, g, b = 0, 255, X
    elif 180 <= h < 240:
        r, g, b = 0, X, 255
    elif 240 <= h < 300:
        r, g, b = X, 0, 255
    else:
        r, g, b = 255, 0, X

    return int(r), int(g), int(b)

i2c = I2C(0, scl=Pin(9), sda=Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
# Clear display
oled.fill(0)

# ---- BLYNK VIRTUAL WRITE HANDLER (V1 for Gauge) ----
@blynk.on("V1")
def v1_handler(value):
    try:
        hue = int(value[0])  # Convert Blynk input to integer
        print(f"Recived Hue: {hue}")
        oled.text(f"Hue: {hue}",10,24)
        oled.show()
        r, g, b = hsv_to_rgb(hue)  # Convert HSV to RGB
        set_color(r, g, b)  # Update LED
    except:
        pass

# ---- MAIN LOOP ----
while True:
    blynk.run()
    time.sleep(0.1)