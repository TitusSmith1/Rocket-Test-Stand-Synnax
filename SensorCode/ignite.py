import RPi.GPIO as GPIO
import time

# Configuration
IGNITER_PIN = 27  # GPIO 17 (Physical Pin 11)

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(IGNITER_PIN, GPIO.OUT, initial=GPIO.LOW)

def trigger_ignition(duration=10):
    """
    Activates the MOSFET for a set duration.
    3 seconds is usually plenty to get Nichrome red-hot.
    """
    print(f"!!! WARNING: IGNITION ARMED !!!")
    time.sleep(2) # Safety countdown
    
    print("FIRING...")
    GPIO.output(IGNITER_PIN, GPIO.HIGH) # Turn on MOSFET
    
    time.sleep(duration)
    
    GPIO.output(IGNITER_PIN, GPIO.LOW)  # Turn off MOSFET
    print("IGNITION COMPLETE. MODULE DISARMED.")

try:
    # Run the test
    trigger_ignition()

except KeyboardInterrupt:
    print("\nEMERGENCY STOP")
finally:
    GPIO.cleanup()
