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

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    time.sleep(1)
print("WiFi Connected! IP:", wlan.ifconfig()[0])

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
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + response)
        else:
            html_response = """\
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>ESP32-S3 IoT Weather Station</title>
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
    <h2>ESP32-S3 IoT Weather Station</h2>
    <p>Temperature: <span id='temp'>--</span></p>
    <p>Humidity: <span id='humidity'>--</span></p>
    <p><strong>Alert: <span id='alert'>--</span></strong></p>
</body>
</html>
"""
            conn.send(html_response)
        
        conn.close()

# Run the Web Server and Display Update in Parallel
import _thread
_thread.start_new_thread(update_display_loop, ())  # Start display update thread
start_server()  # Start web server