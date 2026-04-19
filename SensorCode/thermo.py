import spidev
import time

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0) # Bus 0, Device 0 (CE0)
spi.max_speed_hz = 5000000 # 5MHz is plenty for MAX6675

def read_temp():
    # MAX6675 returns two bytes (16 bits)
    raw = spi.readbytes(2)
    
    # Combine bytes: [MSB, LSB]
    # Bit 15 is dummy, Bits 14-3 are the temperature
    value = (raw[0] << 8 | raw[1])
    
    # Check bit 2 (the 'Input Open' flag)
    # If the thermocouple is disconnected, this bit goes high.
    if value & 0x4:
        return "ERROR: Thermocouple Open"
    
    # Shift right 3 bits to get the 12-bit temperature value
    # Each unit represents 0.25 degrees Celsius
    temp = (value >> 3) * 0.25
    return temp

try:
    print("Reading MAX6675 Thermocouple (Ctrl+C to stop)...")
    while True:
        temperature = read_temp()
        if isinstance(temperature, float):
            print(f"Current Temp: {temperature:.2f}°C | {((temperature * 9/5) + 32):.2f}°F")
        else:
            print(temperature)
            
        # The MAX6675 needs ~200ms between conversions
        time.sleep(0.5)

except KeyboardInterrupt:
    spi.close()
    print("\nTest Stopped.")
