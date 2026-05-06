import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# --- CONFIG ---
MAX_PSI = 500
ZERO_V = 0.5
GAIN = 2/3

def to_psi(v):
    # (Voltage - 0.5V offset) * (500 PSI / 4.0V Span)
    p = (v - ZERO_V) * (MAX_PSI / 4.0)
    return max(0, p)

def main():
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        ads.gain = GAIN

        # Using direct integers (0, 1, 2) to bypass library attribute errors
        chan0 = AnalogIn(ads, 0) # Physical Pin A0
        chan1 = AnalogIn(ads, 1) # Physical Pin A1
        chan2 = AnalogIn(ads, 2) # Physical Pin A2

        print(f"\n{'Channel':<10} | {'Raw':<7} | {'Voltage':<8} | {'PSI':<8}")
        print("-" * 45)

        while True:
            # Read all three
            samples = [
                ("A0", chan0.value, chan0.voltage),
                ("A1", chan1.value, chan1.voltage),
                ("A2", chan2.value, chan2.voltage)
            ]

            for name, raw, volt in samples:
                psi = to_psi(volt)
                print(f"{name:<10} | {raw:>7} | {volt:>7.3f}V | {psi:>7.1f}")
            
            print("-" * 45)
            time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
