import pigpio
import time

# Configuration
SERVO_PIN = 23    # GPIO 18 (Physical Pin 12)
MIN_PULSE = 500   # Pulse width for 0 degrees
MAX_PULSE = 2500  # Pulse width for 270 degrees
MAX_ANGLE = 280   # The physical limit of your DS3218

# Initialize pigpio
pi = pigpio.pi()

if not pi.connected:
    print("Could not connect to pigpiod. Did you run 'sudo pigpiod'?")
    exit()

def set_angle(angle):
    """Converts degrees to pulse width and sends to servo."""
    if 0 <= angle <= MAX_ANGLE:
        # Linear interpolation formula:
        # pulse = min + (angle / total_angle) * total_pulse_range
        pulse = MIN_PULSE + (angle / MAX_ANGLE) * (MAX_PULSE - MIN_PULSE)
        pi.set_servo_pulsewidth(SERVO_PIN, pulse)
        print(f"Setting angle to {angle}° ({int(pulse)}µs)")
    else:
        print(f"Angle {angle} is out of range (0-{MAX_ANGLE})")

try:
    print("Starting Servo Test (0 to 90 degrees)...")
    
    while True:
        # Move to 0
        set_angle(0)
        time.sleep(10)
        
        # Move to 90
        set_angle(90)
        time.sleep(10)

except KeyboardInterrupt:
    print("\nCleaning up...")
    # Setting pulsewidth to 0 stops the signal (lets the motor relax)
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()
