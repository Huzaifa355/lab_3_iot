from machine import Pin, I2C
import network
import time
import dht
import ssd1306
import socket
import _thread

# WiFi Credentials
SSID = "Dhanju"
PASSWORD = "Huzaifa355"

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

# Function to Determine Alert Message
def get_alert_message(temp, hum):
    if temp is not None and hum is not None:
        if temp > 30:
            return "It's hot! Stay cool."
        elif temp < 15:
            return "It's cold! Stay warm."
        elif hum < 30:
            return "Air is dry, drink water."
        elif hum > 70:
            return "High humidity! Stay hydrated."
    return "Weather is normal."

# Function to Update OLED Display Continuously
def update_display_loop():
    while True:
        temp, hum = read_sensor()
        alert = get_alert_message(temp, hum)
        
        print(f"Temp: {temp}C, Humidity: {hum}%")  # Debugging Output
        
        display.fill(0)
        display.text(f"Temp: {temp}C", 0, 0)
        display.text(f"Humidity: {hum}%", 0, 16)
        display.text(alert, 0, 32)
        display.show()
        
        time.sleep(2)  # Update every 2 seconds

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Scan Available WiFi Networks
def scan_wifi():
    print("Scanning for WiFi networks...")
    networks = wlan.scan()
    for net in networks:
        ssid = net[0].decode()
        rssi = net[3]
        print(f"SSID: {ssid}, Signal: {rssi} dBm")

scan_wifi()  # Scan before connecting

# Connect to WiFi
wlan.connect(SSID, PASSWORD)
print("Connecting to WiFi...")
timeout = 10  # 10-second timeout
while not wlan.isconnected() and timeout > 0:
    time.sleep(1)
    timeout -= 1

if wlan.isconnected():
    print("WiFi Connected! IP:", wlan.ifconfig()[0])
else:
    print("WiFi connection failed!")
    raise OSError("Failed to connect to WiFi")

# AP Mode Configuration
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32-AP", password="12345678")
print("AP Mode IP:", ap.ifconfig()[0])

# Start Socket-Based Web Server
def start_server():
    addr = ("", 80)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address reuse
    s.bind(addr)
    s.listen(5)
    print("Server is running...")

    while True:
        conn, addr = s.accept()
        print("Connection from:", addr)
        request = conn.recv(1024).decode()
        print("Request:", request)

        if "/data" in request:
            temp, hum = read_sensor()
            alert = get_alert_message(temp, hum)
            response = f'{{"temperature": {temp}, "humidity": {hum}, "alert": "{alert}"}}'
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n".encode() + response.encode())
        else:
            html_response = """
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32-S3 IoT Weather Station</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background: linear-gradient(135deg, #89f7fe, #66a6ff);
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 400px;
            margin: auto;
            background: rgba(255, 255, 255, 0.2);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }
        h2 {
            margin-bottom: 10px;
        }
        p {
            font-size: 20px;
            margin: 10px 0;
        }
        .alert {
            font-weight: bold;
            font-size: 18px;
            color: yellow;
        }
    </style>
    <script>
        async function updateData() {
            let response = await fetch('/data');
            let data = await response.json();
            document.getElementById('temp').innerText = data.temperature + '°C';
            document.getElementById('humidity').innerText = data.humidity + '%';
            document.getElementById('alert').innerText = data.alert;
        }
        setInterval(updateData, 2000);
    </script>
</head>
<body>
    <div class="container">
        <h2>ESP32-S3 IoT Weather Station 🌤️</h2>
        <p>🌡️ Temperature: <span id='temp'>--</span></p>
        <p>💧 Humidity: <span id='humidity'>--</span></p>
        <p class="alert">⚠️ Alert: <span id='alert'>--</span></p>
    </div>
</body>
</html>
"""
            conn.send(html_response.encode())  # Convert to bytes before sending
        
        conn.close()

# Run the Web Server and Display Update in Parallel
_thread.start_new_thread(update_display_loop, ())  # Start display update thread
start_server()  # Start web server
