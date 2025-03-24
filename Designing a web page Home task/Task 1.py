import network
import socket
import time
from machine import Pin, SoftI2C
from neopixel import NeoPixel
import dht
from ssd1306 import SSD1306_I2C

# -----------------------------
# Hardware Setup
# -----------------------------
# NeoPixel RGB LED Setup
pin = Pin(48, Pin.OUT)  # Set GPIO48 to output for NeoPixel
neo = NeoPixel(pin, 1)   # Create NeoPixel driver on GPIO48 for 1 pixel

# DHT11 Sensor Setup
dht_pin = Pin(4)  # DHT11 Data pin (Change if needed)
sensor = dht.DHT11(dht_pin)

# OLED Display Setup
i2c = SoftI2C(scl=Pin(9), sda=Pin(8))  # Adjust based on wiring
oled = SSD1306_I2C(128, 64, i2c)

# -----------------------------
# Wi-Fi Configuration
# -----------------------------
# STA Mode (Connect to an existing network)
ssid = "wifi name "
password = "passowrd"
sta = network.WLAN(network.STA_IF)
sta.active(False)
sta.active(True)
sta.connect(ssid, password)

# Wait for connection
while not sta.isconnected():
    time.sleep(1)
print("Connected to Wi-Fi! IP:", sta.ifconfig()[0])

# AP Mode (Access Point for direct connection)
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32-AP", password="12345678")
print("AP Mode IP:", ap.ifconfig()[0])

# -----------------------------
# Socket Server Setup
# -----------------------------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allows rebinding
s.bind(("0.0.0.0", 80))
s.listen(5)

# -----------------------------
# Helper Functions
# -----------------------------
def display_message_on_oled(msg):
    """Displays a given message on the OLED screen."""
    oled.fill(0)
    max_chars_per_line = 16
    max_chars_total = 64  # Max 4 lines (16 chars each)

    # Limit total characters
    msg = msg[:max_chars_total]

    # Split message into words and then lines
    words = msg.split(" ")
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + (1 if current_line else 0) <= max_chars_per_line:
            current_line += (" " if current_line else "") + word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    # Display only up to 4 lines
    y = 0
    for line in lines[:4]:
        oled.text(line, 5, y)
        y += 16

    oled.show()

def web_page():
    """Generates the HTML webpage with enhanced CSS."""
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* Global Styles */
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #74ABE2, #5563DE);
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        /* Container */
        .container {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.25);
            padding: 30px;
            max-width: 400px;
            width: 90%;
        }}
        /* Headings */
        h1 {{
            margin-bottom: 20px;
            color: #5563DE;
        }}
        h2 {{
            margin-top: 30px;
            color: #333;
        }}
        /* Text and Paragraphs */
        p {{
            font-size: 16px;
            margin: 10px 0;
        }}
        /* Form Elements */
        label {{
            font-weight: bold;
        }}
        input[type="range"] {{
            width: 70%;
            margin: 5px 0;
        }}
        input[type="number"] {{
            width: 20%;
            padding: 5px;
            margin: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
            text-align: center;
        }}
        input[type="text"] {{
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
        }}
        button {{
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            border: none;
            background: #5563DE;
            color: #fff;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s ease;
        }}
        button:hover {{
            background: #4453C0;
        }}
        /* Responsive Design */
        @media (max-width: 480px) {{
            .container {{
                padding: 20px;
            }}
            h1 {{
                font-size: 24px;
            }}
        }}
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

# -----------------------------
# Main Server Loop
# -----------------------------
while True:
    conn, addr = s.accept()
    print("Connection from:", addr)
    try:
        request = conn.recv(1024).decode()
        if not request:
            conn.close()
            continue

        print("Request:", request)
        
        # Handle RGB Color Control
        if "/?r=" in request and "&g=" in request and "&b=" in request:
            try:
                parts = request.split("/?")[1].split(" ")[0]
                params = {kv.split("=")[0]: kv.split("=")[1] for kv in parts.split("&")}
                r = min(255, max(0, int(params.get("r", 0))))
                g = min(255, max(0, int(params.get("g", 0))))
                b = min(255, max(0, int(params.get("b", 0))))
                neo[0] = (r, g, b)
                neo.write()
            except Exception as e:
                print("Invalid RGB Input:", e)

        # Handle OLED Message Display
        elif "/?msg=" in request:
            try:
                msg = request.split("/?msg=")[1].split(" ")[0]
                msg = msg.replace("%20", " ")
                display_message_on_oled(msg)
            except Exception as e:
                print("Invalid OLED Message:", e)

        response = web_page()
        try:
            conn.sendall(("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response).encode())
        except OSError as e:
            print("Error sending response:", e)
    except Exception as e:
        print("Error processing request:", e)
    finally:
        conn.close()

