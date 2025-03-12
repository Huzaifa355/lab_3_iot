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

# Scan Available WiFi Networks
def scan_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("Scanning for WiFi networks...")
    networks = wlan.scan()
    for net in networks:
        ssid = net[0].decode()
        rssi = net[3]
        print(f"SSID: {ssid}, Signal: {rssi} dBm")

scan_wifi()  # Scan before connecting

# Wi-Fi Configuration (STA Mode)
ssid = "Dhanju"
password = "Huzaifa3550"
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

# Socket Programming
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 80))
s.listen(5)

# Function to Display Message on OLED
def display_message_on_oled(msg):
    oled.fill(0)
    max_chars_per_line = 16
    max_chars_total = 64  # Max 4 lines (16 chars each)
    msg = msg[:max_chars_total]
    words = msg.split(" ")
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars_per_line:
            current_line += (" " if current_line else "") + word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    y = 0
    for line in lines[:4]:
        oled.text(line, 5, y)
        y += 16  
    oled.show()

# Web Page Function
def web_page():
    try:
        sensor.measure()
        temp = sensor.temperature()
        humidity = sensor.humidity()
    except:
        temp = "N/A"
        humidity = "N/A"
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 WebServer</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; background: linear-gradient(135deg, #74ebd5, #acb6e5); height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }}
            .container {{ max-width: 420px; padding: 20px; background: rgba(255, 255, 255, 0.9); border-radius: 12px; box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.2); backdrop-filter: blur(10px); }}
            h1 {{ color: #333; font-size: 22px; }}
            p {{ font-size: 16px; color: #555; }}
            input[type="range"], input[type="number"] {{ width: 80px; margin: 5px; }}
            input[type="number"] {{ text-align: center; }}
            button {{ width: 100%; margin-top: 12px; padding: 12px; border: none; border-radius: 6px; background: #008CBA; color: white; font-size: 16px; cursor: pointer; transition: 0.3s; }}
            button:hover {{ background: #005f73; }}
            .color-preview {{ margin-top: 10px; height: 40px; width: 100%; border-radius: 6px; border: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESP32 RGB LED Control</h1>
            <p>Temperature: {temp}°C | Humidity: {humidity}%</p>
            <div class="color-preview" id="colorBox"></div>
            <button onclick="setColor()">Set Color</button>
        </div>
    </body>
    </html>"""
    return html

while True:
    conn, addr = s.accept()
    print("Connection from:", addr)
    request = conn.recv(1024).decode()
    print("Request:", request)
    if "/?r=" in request and "&g=" in request and "&b=" in request:
        try:
            parts = request.split("/?")[1].split(" ")[0]
            params = {kv.split("=")[0]: kv.split("=")[1] for kv in parts.split("&")}
            r, g, b = min(255, max(0, int(params["r"]))), min(255, max(0, int(params["g"]))), min(255, max(0, int(params["b"])))
            neo[0] = (r, g, b)
            neo.write()
        except:
            print("Invalid RGB Input")
    elif "/?msg=" in request:
        try:
            msg = request.split("/?msg=")[1].split(" ")[0]
            msg = msg.replace("%20", " ")
            display_message_on_oled(msg)
        except:
            print("Invalid OLED Message")
    response = web_page()
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response)
    conn.close()
