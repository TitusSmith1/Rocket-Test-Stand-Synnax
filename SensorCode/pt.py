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

# ------------------------
# PRESSURE TRANSDUCER CLASS
# ------------------------
class PressureTransducer:
    """Class to manage a single pressure transducer on a specific ADC channel."""
    
    def __init__(self, channel, max_pressure=500.0, name="PT"):
        """
        Args:
            channel: ADC channel number (0-3)
            max_pressure: Maximum pressure in PSI
            name: Name identifier for this PT
        """
        self.channel = channel
        self.analog_in = AnalogIn(ads, channel)
        self.max_pressure = max_pressure
        self.name = name
        
        # Sensor characteristics
        self.zero_v = 0.5
        self.full_scale_v = 4.5
        self.divider_ratio = 1
    
    def get_pressure(self):
        """Read and return pressure in PSI."""
        raw_v = self.analog_in.voltage
        sensor_v = raw_v / self.divider_ratio
        sensor_v = max(0, sensor_v)
        psi = (sensor_v - self.zero_v) * (self.max_pressure / (self.full_scale_v - self.zero_v))
        return max(0, psi)
    
    def get_voltage(self):
        """Get raw voltage reading."""
        return self.analog_in.voltage


# Dictionary to store multiple PT instances
_pt_instances = {}

def get_pressure(ads_voltage):
    """Legacy function for backward compatibility."""
    sensor_v = ads_voltage / 1
    sensor_v = max(0, sensor_v)
    psi = (sensor_v - 0.5) * (500.0 / (4.5 - 0.5))
    return max(0, psi)


def create_pt(channel, max_pressure=500.0, name=None):
    """
    Create and register a new pressure transducer.
    
    Args:
        channel: ADC channel number (0-3)
        max_pressure: Maximum pressure in PSI
        name: Optional name (defaults to PT{channel})
    
    Returns:
        PressureTransducer instance
    """
    if name is None:
        name = f"PT{channel}"
    
    pt_instance = PressureTransducer(channel, max_pressure, name)
    _pt_instances[name] = pt_instance
    return pt_instance


def get_pt(name):
    """Get a PT instance by name."""
    return _pt_instances.get(name)


def get_all_pts():
    """Get all registered PT instances."""
    return _pt_instances


# Legacy: create default instance for backward compatibility
chan = AnalogIn(ads, 0)


def main():
    # ------------------------
    # MAIN LOOP - DEMO
    # ------------------------
    print("Starting Pressure Readings...")
    print("-" * 40)

    # Create multiple PTs
    pt1 = create_pt(0, 500.0, "PT1")
    pt2 = create_pt(1, 300.0, "PT2")
    pt3 = create_pt(2, 100.0, "PT3")

    try:
        while True:
            for name, pt in get_all_pts().items():
                psi = pt.get_pressure()
                print(f"{name}: {psi:.1f} PSI")
            print("-" * 40)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()