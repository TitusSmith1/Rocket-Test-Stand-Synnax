import time
import sys
import RPi.GPIO as GPIO
from hx711 import HX711

# Silence the "channel already in use" warnings from previous crashes
GPIO.setwarnings(False)

# Set up the GPIO pin numbering mode
GPIO.setmode(GPIO.BCM)

# Pin configuration from your wiring
DAT_PIN = 6
CLK_PIN = 5

def get_average_reading(hx, num_readings=5):
    """Fetches raw data from the sensor safely."""
    
    # Passing the argument positionally avoids the keyword TypeError!
    raw_data = hx.get_raw_data(num_readings)
    
    # Handle if the library version returns a list of readings
    if isinstance(raw_data, list):
        valid_data = [val for val in raw_data if isinstance(val, (int, float))]
        if not valid_data:
            return 0
        return sum(valid_data) / len(valid_data)
        
    # Handle if the library version returns a single averaged number (or False)
    if raw_data is not False and isinstance(raw_data, (int, float)):
        return raw_data
        
    return 0

def setup_scale():
    print("Initializing the scale...")
    
    # Initialize the HX711 object
    hx = HX711(dout_pin=DAT_PIN, pd_sck_pin=CLK_PIN)
    hx.reset()
    
    print("Taring the scale. Please make sure it is empty...")
    time.sleep(1) # Give the sensor a moment to settle
    
    # Calculate the "Tare" (the raw weight of the empty scale)
    tare_offset = get_average_reading(hx, 10)
    print(f"Tare complete! Zero offset is: {tare_offset}")
    
    return hx, tare_offset

def main():
    hx, tare_offset = setup_scale()
    
    # ==========================================
    # CALIBRATION (The "Reference Unit")
    # ==========================================
    # 1. Leave this at 1 for your first run.
    # 2. Place a known weight on the scale (e.g., exactly 1000g).
    # 3. Look at the Current Weight printed in the console.
    # 4. Divide that console number by your known weight.
    # 5. Change the '1' below to your new calculated number.
    # ==========================================
    reference_unit = 1 
    
    try:
        while True:
            # Get the current raw data
            current_raw = get_average_reading(hx, 5)
            
            # Subtract the tare offset, then divide by the calibration unit
            weight = (current_raw - tare_offset) / reference_unit
            
            print(f"Current Weight: {weight:.2f}")
            time.sleep(0.5)

    except (KeyboardInterrupt, SystemExit):
        print("\nExiting program and cleaning up GPIO pins...")
    finally:
        GPIO.cleanup()
        sys.exit()

if __name__ == "__main__":
    main()
