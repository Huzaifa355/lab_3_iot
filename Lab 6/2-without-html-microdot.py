# 2-rgb on off  using microdot without html code
from microdot import Microdot, Response
from machine import Pin
from neopixel import NeoPixel

# Define the pin connected to the NeoPixel
pin = Pin(48, Pin.OUT)
np = NeoPixel(pin, 1)  # 1 NeoPixel

# Function to set RGB color
def set_rgb(r, g, b):
    np[0] = (r, g, b)  # Set the color for the first NeoPixel
    np.write()  # Write the color to the NeoPixel

app = Microdot()
# Initialize the Microdot web server
@app.route('/')
def index(request):
    return 'Hello, World!'

@app.route('/rgb/<state>')
def led_control(request, state):
    if state == 'on':
        # Turn on LED (assuming it's connected to GPIO 2)
        set_rgb(255,0,0)
        return 'RGB LED turned ON'
    elif state == 'off':
        # Turn off LED
        set_rgb(0,0,0)
        return 'RGB LED turned OFF'
    else:
        return 'Invalid state'


# Start the Microdot Web Server
print("Starting server...")
#app.run(host="0.0.0.0", port=80)
app.run(port=80)
