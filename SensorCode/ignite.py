import RPi.GPIO as GPIO
import time
import threading

# Configuration
IGNITER_PIN = 27  # GPIO 17 (Physical Pin 11)

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(IGNITER_PIN, GPIO.OUT, initial=GPIO.LOW)
_off_timer = None
_timer_lock = threading.Lock()
_is_on = False

def _turn_off():
    global _off_timer
    with _timer_lock:
        GPIO.output(IGNITER_PIN, GPIO.LOW)
        _off_timer = None
        global _is_on
        _is_on = False
    print("IGNITION COMPLETE. MODULE DISARMED.")


def trigger_ignition(duration=3):
    """
    Activates the MOSFET for a set duration.
    3 seconds is usually plenty to get Nichrome red-hot.
    """
    print(f"!!! WARNING: IGNITION ARMED !!!")

    print("FIRING...")
    GPIO.output(IGNITER_PIN, GPIO.HIGH)  # Turn on MOSFET
    global _is_on
    _is_on = True

    # Schedule a non-blocking turn-off after `duration` seconds.
    global _off_timer
    with _timer_lock:
        # cancel any existing timer
        if _off_timer is not None:
            _off_timer.cancel()
        _off_timer = threading.Timer(duration, _turn_off)
        _off_timer.daemon = True
        _off_timer.start()
    

def cancel_ignition():
    global _off_timer
    with _timer_lock:
        if _off_timer is not None:
            _off_timer.cancel()
            _off_timer = None
    GPIO.output(IGNITER_PIN, GPIO.LOW)
    global _is_on
    _is_on = False
    print("IGNITION CANCELLED. MODULE DISARMED.")


def is_igniter_on():
    """Return True if the igniter MOSFET is currently driven HIGH."""
    with _timer_lock:
        return bool(_is_on)


if __name__=="__main__":
    try:
        # Run the test
        trigger_ignition()
        # Let the program run a bit so the timer can fire in this demo.
        time.sleep(5)
        cancel_ignition()

    except KeyboardInterrupt:
        print("\nEMERGENCY STOP")
    finally:
        # Ensure timer is cancelled and GPIO cleaned up
        with _timer_lock:
            if _off_timer is not None:
                _off_timer.cancel()
                _off_timer = None
        GPIO.cleanup()
