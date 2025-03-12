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
#socket programing
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allows rebinding
s.bind(("0.0.0.0", 80))
s.listen(5)

# Function to Display Message on OLED
def display_message_on_oled(msg):
    oled.fill(0)
    max_chars_per_line = 16
    max_chars_total = 64  # Max 4 lines (16 chars each)

    # Limit total characters
    msg = msg[:max_chars_total]

    # Split words properly
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

    # Display only 4 lines max
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
            body {{ font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f4; }}
            h1 {{ color: #333; }}
            .container {{ max-width: 400px; margin: auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.2); }}
            input[type="range"], input[type="number"] {{ width: 80px; margin: 5px; }}
            input[type="number"] {{ text-align: center; }}
            button {{ margin-top: 10px; padding: 10px; border: none; background: #008CBA; color: white; font-size: 16px; cursor: pointer; }}
            button:hover {{ background: #005f73; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESP32 RGB LED Control</h1>
            <p>Temperature: {temp}°C | Humidity: {humidity}%</p>

            <label>Red:</label>
            <input type="range" id="red" min="0" max="255" value="0" oninput="updateRGB('red')">
            <input type="number" id="redValue" min="0" max="255" value="0" oninput="syncRGB('red')"><br>

            <label>Green:</label>
            <input type="range" id="green" min="0" max="255" value="0" oninput="updateRGB('green')">
            <input type="number" id="greenValue" min="0" max="255" value="0" oninput="syncRGB('green')"><br>

            <label>Blue:</label>
            <input type="range" id="blue" min="0" max="255" value="0" oninput="updateRGB('blue')">
            <input type="number" id="blueValue" min="0" max="255" value="0" oninput="syncRGB('blue')"><br>

            <button onclick="setColor()">Set Color</button>

            <h2>OLED Message</h2>
            <input type="text" id="msg" placeholder="Enter message (Max 64 chars)" maxlength="64">
            <button onclick="sendMessage()">Send to OLED</button>
        </div>

        <script>
            function updateRGB(color) {{
                let value = document.getElementById(color).value;
                document.getElementById(color + "Value").value = value;
            }}

            function syncRGB(color) {{
                let value = document.getElementById(color + "Value").value;
                if (value > 255) {{ value = 255; }}
                if (value < 0) {{ value = 0; }}
                document.getElementById(color + "Value").value = value;
                document.getElementById(color).value = value;
            }}

            function setColor() {{
                let r = document.getElementById("red").value;
                let g = document.getElementById("green").value;
                let b = document.getElementById("blue").value;
                fetch("/?r=" + r + "&g=" + g + "&b=" + b);
            }}

            function sendMessage() {{
                let msg = document.getElementById("msg").value;
                fetch("/?msg=" + encodeURIComponent(msg));
            }}
        </script>
    </body>
    </html>"""
    return html

while True:
    conn, addr = s.accept()
    print("Connection from:", addr)
    request = conn.recv(1024).decode()
    print("Request:", request)
    
    
     # RGB Color Control
    if "/?r=" in request and "&g=" in request and "&b=" in request:
        try:
            parts = request.split("/?")[1].split(" ")[0]  
            params = {kv.split("=")[0]: kv.split("=")[1] for kv in parts.split("&")}
            r, g, b = min(255, max(0, int(params["r"]))), min(255, max(0, int(params["g"]))), min(255, max(0, int(params["b"])))
            neo[0] = (r, g, b)
            neo.write()
        except:
            print("Invalid RGB Input")

    # OLED Message Display
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

    