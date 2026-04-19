import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# ------------------------
# I2C + ADC SETUP
# ------------------------
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

ads.gain = 1  # ±4.096V range (safe for your divider output)

chan = AnalogIn(ads, 0)

# ------------------------
# SENSOR CONFIG
# ------------------------
MAX_PRESSURE = 500.0   # change to 300.0 if using 300 PSI sensor
DIVIDER_RATIO = 1

# industrial sensor characteristics
ZERO_V = 0.5
FULL_SCALE_V = 4.5

# ------------------------
# PRESSURE CONVERSION
# ------------------------
def get_pressure(ads_voltage):
    # undo divider
    sensor_v = ads_voltage / DIVIDER_RATIO

    # clamp noise
    sensor_v = max(0, sensor_v)

    # convert voltage → PSI
    psi = (sensor_v - ZERO_V) * (MAX_PRESSURE / (FULL_SCALE_V - ZERO_V))

    return max(0, psi)


def main():
    # ------------------------
    # MAIN LOOP
    # ------------------------
    print("Starting Pressure Readings...")
    print(f"Max Pressure: {MAX_PRESSURE} PSI")
    print(f"Divider Ratio: {DIVIDER_RATIO:.4f}")
    print("-" * 40)

    try:
        while True:
            raw_v = chan.voltage
            psi = get_pressure(raw_v)

            sensor_v = raw_v / DIVIDER_RATIO

            print(f"ADC: {raw_v:.3f} V | Sensor: {sensor_v:.3f} V | Pressure: {psi:.1f} PSI")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()