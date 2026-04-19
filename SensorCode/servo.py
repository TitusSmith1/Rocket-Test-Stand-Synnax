import pigpio
import time

# Initialize pigpio (do this once)
pi = pigpio.pi()

if not pi.connected:
    print("Could not connect to pigpiod. Did you run 'sudo pigpiod'?")
    exit()

# ------------------------
# SERVO CLASS
# ------------------------
class Servo:
    """Class to manage a single servo on a specific GPIO pin."""
    
    def __init__(self, pin, min_pulse=500, max_pulse=2500, max_angle=280, name=None):
        """
        Args:
            pin: GPIO pin number
            min_pulse: Minimum pulse width in microseconds
            max_pulse: Maximum pulse width in microseconds
            max_angle: Maximum angle in degrees
            name: Optional name identifier
        """
        self.pin = pin
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.max_angle = max_angle
        self.name = name if name else f"Servo_{pin}"
        
        # Initialize the pin as output
        pi.set_mode(pin, pigpio.OUTPUT)
    
    def set_angle(self, angle):
        """Set the servo to a specific angle."""
        if 0 <= angle <= self.max_angle:
            pulse = self.min_pulse + (angle / self.max_angle) * (self.max_pulse - self.min_pulse)
            pi.set_servo_pulsewidth(self.pin, int(pulse))
            print(f"{self.name}: Setting angle to {angle}° ({int(pulse)}µs)")
        else:
            print(f"{self.name}: Angle {angle} is out of range (0-{self.max_angle})")
    
    def stop(self):
        """Stop the servo (disable pulse)."""
        pi.set_servo_pulsewidth(self.pin, 0)
    
    def cleanup(self):
        """Stop the servo and clean up."""
        self.stop()


# Dictionary to store multiple servo instances
_servo_instances = {}


def create_servo(pin, min_pulse=500, max_pulse=2500, max_angle=280, name=None):
    """
    Create and register a new servo.
    
    Args:
        pin: GPIO pin number
        min_pulse: Minimum pulse width in microseconds
        max_pulse: Maximum pulse width in microseconds
        max_angle: Maximum angle in degrees
        name: Optional name (defaults to Servo_{pin})
    
    Returns:
        Servo instance
    """
    if name is None:
        name = f"Servo_{pin}"
    
    servo_instance = Servo(pin, min_pulse, max_pulse, max_angle, name)
    _servo_instances[name] = servo_instance
    return servo_instance


def get_servo(name):
    """Get a servo instance by name."""
    return _servo_instances.get(name)


def get_all_servos():
    """Get all registered servo instances."""
    return _servo_instances


def cleanup_all():
    """Stop all servos and clean up pigpio."""
    for servo in _servo_instances.values():
        servo.cleanup()
    pi.stop()


# Legacy: create default instance for backward compatibility
SERVO_PIN = 23

def set_angle(angle):
    """Legacy function for backward compatibility."""
    if 0 <= angle <= 280:
        pulse = 500 + (angle / 280) * (2500 - 500)
        pi.set_servo_pulsewidth(SERVO_PIN, pulse)
        print(f"Setting angle to {angle}° ({int(pulse)}µs)")
    else:
        print(f"Angle {angle} is out of range (0-280)")


def cleanup():
    """Legacy cleanup function."""
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()


def main():
    # Create multiple servos
    servo1 = create_servo(23, name="Servo_1")
    servo2 = create_servo(24, name="Servo_2")
    servo3 = create_servo(18, name="Servo_3")

    try:
        print("Starting Servo Test...")
        while True:
            # Test all servos
            for name, s in get_all_servos().items():
                s.set_angle(90)
            time.sleep(2)
            for name, s in get_all_servos().items():
                s.set_angle(0)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nCleaning up...")
        cleanup_all()

if __name__ == "__main__":
    main()