print("Hello, ESP32-S3!")

from machine import Pin, I2C, Timer
import machine
import ssd1306 
import dht
import time

DHT_PIN = 4  # DHT22 data pin
button = Pin(0, Pin.IN, Pin.PULL_UP)
dht_sensor = dht.DHT11(machine.Pin(DHT_PIN))

# Initialize I2C for OLED
i2c = machine.I2C(scl=machine.Pin(9), sda=machine.Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

pressed = False
debounce_timer = None

def button_pressed(pin):
    global debounce_timer, pressed

    if debounce_timer is None:
        pressed = not pressed
        if pressed:
            oled.poweroff()
        else:
            oled.poweron()

        debounce_timer = Timer(0)
        debounce_timer.init(mode=Timer.ONE_SHOT, period=200, callback=debounce_callback)

def debounce_callback(timer):
    global debounce_timer
    debounce_timer = None

button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

# Function to draw thermometer icon
def draw_thermometer(x, y):
    # Manually draw using pixels
    for i in range(6):
        oled.pixel(x+2, y+i, 1)  # Thermometer stem
    oled.pixel(x+1, y+6, 1)
    oled.pixel(x+3, y+6, 1)
    oled.pixel(x, y+7, 1)
    oled.pixel(x+4, y+7, 1)
    oled.pixel(x+2, y+7, 1)  # Bulb bottom

# Function to draw a droplet icon
def draw_droplet(x, y):
    oled.pixel(x+2, y, 1)
    oled.pixel(x+1, y+1, 1)
    oled.pixel(x+3, y+1, 1)
    oled.pixel(x, y+2, 1)
    oled.pixel(x+4, y+2, 1)
    oled.pixel(x+2, y+3, 1)
    for i in range(3):
        oled.pixel(x+1+i, y+4, 1)

# Main loop
while True:
    try:
        dht_sensor.measure()
        time.sleep(2)
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        print("Temp:", temp, "C")
        print("Humidity:", humidity, "%")

        oled.fill(0)
        
        # Draw thermometer icon
        draw_thermometer(0, 0)
        oled.text("{} C".format(temp), 10, 0)

        # Draw droplet icon
        draw_droplet(0, 32)
        oled.text("{}%".format(humidity), 10, 32)

        oled.show()

    except Exception as e:
        print("Error reading DHT11 sensor:", e)
    
    time.sleep(1)  # Update every second
