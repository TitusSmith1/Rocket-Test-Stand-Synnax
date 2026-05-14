import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# 1. Initialize the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# 2. Create the PCA9685 class instance
pca = PCA9685(i2c)

# 3. Set the PWM frequency to 50Hz (the standard for most servos)
pca.frequency = 50

# 4. Initialize the servo on channel 8
# The PCA9685 has 16 channels, indexed 0 to 15.
servo_8 = servo.Servo(pca.channels[9])

print("Starting servo test on Channel 8. Press Ctrl+C to stop.")

try:
    while True:
        print("Moving to 0 degrees")
        servo_8.angle = 0
        time.sleep(5)
        
        print("Moving to 90 degrees")
        servo_8.angle = 90
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\nTest stopped by user.")

finally:
    # Safely de-initialize the hardware on exit
    pca.deinit()
    print("PCA9685 de-initialized.")
