# lab4 rgb-web.py into microdot
# 3-rgb 3 color setting using microdot with simple html
from microdot import Microdot
from machine import Pin
from neopixel import NeoPixel

# Constants
RGB_COLORS = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
}

# Initialize the NeoPixel
pin = Pin(48, Pin.OUT)
neo = NeoPixel(pin, 1)  # 1 NeoPixel

# Function to set RGB color
def set_rgb(color):
    if color in RGB_COLORS:
        neo[0] = RGB_COLORS[color]  # Set the color for the first NeoPixel
        neo.write()  # Write the color to the NeoPixel
    else:
        raise ValueError(f"Invalid color: {color}")

# HTML for the web page
def web_page():
    return """<!DOCTYPE html>
<html>
<head><title>ESP32 RGB LED Control</title></head>
<body>
<h1>ESP32 RGB LED Control</h1>
<p><a href="/rgb/red"><button>Turn RGB RED</button></a></p>
<p><a href="/rgb/green"><button>Turn RGB GREEN</button></a></p>
<p><a href="/rgb/blue"><button>Turn RGB BLUE</button></a></p>
</body>
</html>"""

# Initialize MicroDot app
app = Microdot()

# Root route to serve the web page
@app.route('/')
def index(request):
    return web_page(), 200, {'Content-Type': 'text/html'}

# Route to handle RGB color changes
@app.route('/rgb/<color>')
def set_color(request, color):
    try:
        set_rgb(color)  # Set the NeoPixel color
        return web_page(), 200, {'Content-Type': 'text/html'}
    except ValueError as e:
        return str(e), 400  # Return error message for invalid color

# Start the MicroDot web server
# Start the Microdot Web Server
print("Starting server...")
app.run(port=80)
