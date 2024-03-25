# botton.py
import RPi.GPIO as GPIO
import time
from Measure import perform_measurement

# Define the GPIO pin number for the button to GPIO 13
GPIO.setmode(GPIO.BCM)
button_pin = 13 

# Set up the GPIO pin mode
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize the measuring state as True, indicating that measurement starts
measuring = True

def button_callback(channel):
    # Toggle the measuring state
    measuring = not measuring
    if measuring:
        print("Measuring resumed.")
    else:
        print("Measuring paused.")

# Set up event detection: detect falling edge, and debounce with bouncetime
GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=button_callback, bouncetime=300)

# Main
try:
    while True:
        # Execute only when measuring is True
        if measuring:
            perform_measurement()
        else:
            # When measurement is paused, you can perform some logic here
            pass
        # Measurement delay 1s
        time.sleep(1)
finally:
    GPIO.cleanup()