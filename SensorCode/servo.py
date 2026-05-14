import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo as servo_motor

# Initialize PCA9685 over I2C
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

# ------------------------
# SERVO CLASS
# ------------------------
class Servo:
    """Class to manage a single servo on a specific GPIO pin."""
    
    def __init__(self, channel, min_pulse=500, max_pulse=2500, max_angle=180, name=None):
        """
        Args:
            channel: PCA9685 channel object
            min_pulse: Minimum pulse width in microseconds
            max_pulse: Maximum pulse width in microseconds
            max_angle: Maximum angle in degrees
            name: Optional name identifier
        """
        self.channel = channel
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.max_angle = max_angle
        self.name = name if name else f"Servo_{channel.channel}"
        self._servo = servo_motor.Servo(channel, min_pulse=min_pulse, max_pulse=max_pulse)

    def set_angle(self, angle):
        """Set the servo to a specific angle."""
        if 0 <= angle <= self.max_angle:
            self._servo.angle = angle
            print(f"{self.name}: Setting angle to {angle}°")
        else:
            print(f"{self.name}: Angle {angle} is out of range (0-{self.max_angle})")

    def stop(self):
        """Stop the servo (disable pulses)."""
        self._servo.angle = None

    def cleanup(self):
        """Stop the servo and clean up."""
        self.stop()


# Dictionary to store multiple servo instances
_servo_instances = {}


def create_servo(channel, min_pulse=500, max_pulse=2500, max_angle=180, name=None):
    """
    Create and register a new servo on the PCA9685.
    
    Args:
        channel: PCA9685 channel number (0-15)
        min_pulse: Minimum pulse width in microseconds
        max_pulse: Maximum pulse width in microseconds
        max_angle: Maximum angle in degrees
        name: Optional name (defaults to Servo_{channel})
    
    Returns:
        Servo instance
    """
    if name is None:
        name = f"Servo_{channel}"
    
    servo_instance = Servo(
        pca.channels[channel],
        min_pulse=min_pulse,
        max_pulse=max_pulse,
        max_angle=max_angle,
        name=name,
    )
    _servo_instances[name] = servo_instance
    return servo_instance


def get_servo(name):
    """Get a servo instance by name."""
    return _servo_instances.get(name)


def get_all_servos():
    """Get all registered servo instances."""
    return _servo_instances


def cleanup_all():
    """Stop all servos and deinitialize the PCA9685."""
    for servo_instance in _servo_instances.values():
        servo_instance.cleanup()
    pca.deinit()


# Legacy: create default instance for backward compatibility
SERVO_PIN = 23

def set_angle(angle):
    """Legacy function for backward compatibility."""
    if 0 <= angle <= 180:
        servo = get_servo(f"Servo_{SERVO_PIN}")
        if servo:
            servo.set_angle(angle)
            print(f"Setting angle to {angle}°")
        else:
            print("Legacy servo instance not found.")
    else:
        print(f"Angle {angle} is out of range (0-180)")


def cleanup():
    """Legacy cleanup function."""
    cleanup_all()


def main():
    # Create multiple servos on PCA9685 channels 8, 9, and 10
    servo1 = create_servo(8, name="Servo_1")
    servo2 = create_servo(9, name="Servo_2")
    servo3 = create_servo(10, name="Servo_3")

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