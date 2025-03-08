import network
import time
import BlynkLib
import neopixel
import machine
import ssd1306
from machine import Pin, I2C

# ---- CONFIGURATION ----
WIFI_CREDENTIALS = {"SSID": "Huzaifa", "PASSWORD": "12345678"}
BLYNK_AUTH_TOKEN = "p17kdKvaFFK5kXxMnzGNtjPtXDrXP6Xq"

# NeoPixel LED setup
LED_PIN = 48
LED_COUNT = 1

# ---- WIFI CONNECTION ----
def establish_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to Wi-Fi: {WIFI_CREDENTIALS['SSID']}")
        wlan.connect(WIFI_CREDENTIALS["SSID"], WIFI_CREDENTIALS["PASSWORD"])
        while not wlan.isconnected():
            time.sleep(1)
    print("Wi-Fi Connected! IP Address:", wlan.ifconfig()[0])

establish_wifi()

# ---- INITIALIZING BLYNK ----
blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN, server="blynk.cloud", port=80, insecure=True)

@blynk.on("connected")
def on_blynk_connect():
    print("✅ Connected to Blynk!")

@blynk.on("disconnected")
def on_blynk_disconnect():
    print("❌ Blynk Connection Lost!")

# ---- LED CONTROL ----
np = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)

def update_led_color(red, green, blue):
    np[0] = (red, green, blue)
    np.write()
    print(f"LED Updated: R={red}, G={green}, B={blue}")

# ---- HUE TO RGB CONVERSION ----
def hue_to_rgb(hue):
    """ Converts a hue value (0-255) to RGB (0-255). """
    hue = hue / 255.0 * 360
    x = (1 - abs((hue / 60) % 2 - 1)) * 255

    if 0 <= hue < 60:
        r, g, b = 255, x, 0
    elif 60 <= hue < 120:
        r, g, b = x, 255, 0
    elif 120 <= hue < 180:
        r, g, b = 0, 255, x
    elif 180 <= hue < 240:
        r, g, b = 0, x, 255
    elif 240 <= hue < 300:
        r, g, b = x, 0, 255
    else:
        r, g, b = 255, 0, x

    return int(r), int(g), int(b)

# ---- OLED SETUP ----
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)

# ---- BLYNK INPUT HANDLER (V1) ----
@blynk.on("V1")
def handle_v1(value):
    try:
        hue_value = int(value[0])
        print(f"Received Hue: {hue_value}")
        oled.fill(0)
        oled.text(f"Hue: {hue_value}", 10, 24)
        oled.show()
        red, green, blue = hue_to_rgb(hue_value)
        update_led_color(red, green, blue)
    except Exception as e:
        print("Error processing hue input:", e)

# ---- MAIN LOOP ----
while True:
    blynk.run()
    time.sleep(0.1)
