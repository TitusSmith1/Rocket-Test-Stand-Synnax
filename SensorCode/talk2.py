import RPi.GPIO as GPIO
import synnax as sy
import socket
import sys
import time

# --- CONFIGURATION ---
IGNITER_PIN = 18 
PORT = 9090       
SUBNET = "192.168.172"

# --- GPIO SETUP ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(IGNITER_PIN, GPIO.OUT, initial=GPIO.LOW)

def discover_pc_ip(subnet, port):
    print(f"Scanning {subnet}.1 to {subnet}.254...")
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.02) 
            if s.connect_ex((ip, port)) == 0:
                return ip
    return None

def main():
    print("--- Starting Synnax Control ---")
    
    pc_ip = discover_pc_ip(SUBNET, PORT)
    if not pc_ip:
        print("Error: PC not found.")
        sys.exit(1)
        
    print(f"Found PC at {pc_ip}")

    try:
        client = sy.Synnax(
            host=pc_ip,
            port=PORT,
            username="synnax",
            password="seldon",
            secure=False
        )
        print("Connected!")

        # 1. Setup Time Channel
        try:
            # Trying positional argument instead of keyword 'name'
            t_chan = client.channels.retrieve("test_time2")
            print("Found existing time channel.")
        except:
            try:
                t_chan = client.channels.create(
                    name="test_time2", 
                    data_type=sy.DataType.TIMESTAMP, 
                    is_index=True
                )
                print("Created new time channel.")
            except Exception as e:
                if "already exists" in str(e).lower():
                    # Last ditch effort: if it exists, try to get it again
                    t_chan = client.channels.retrieve("test_time2")
                    print("Recovered existing time channel.")
                else:
                    raise e

        # 2. Setup Data Channel
        try:
            d_chan = client.channels.retrieve("test_temperature")
            print("Found existing temperature channel.")
        except:
            try:
                d_chan = client.channels.create(
                    name="test_temperature", 
                    data_type=sy.DataType.FLOAT32, 
                    index=t_chan.key
                )
                print("Created new temperature channel.")
            except Exception as e:
                if "already exists" in str(e).lower():
                    d_chan = client.channels.retrieve("test_temperature")
                    print("Recovered existing temperature channel.")
                else:
                    raise e

        print(f"\n--- System Ready ---")
        print(f"Index: {t_chan.name} | Data: {d_chan.name}")
        
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"Synnax Error: {e}")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        GPIO.cleanup()
        print("GPIO Cleaned.")

if __name__ == "__main__":
    main()
