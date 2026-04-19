import pigpio
import synnax as sy
import socket
import sys
import time

# --- CONFIGURATION ---
SERVO_PIN = 23    # Must match your working hardware setup!
PORT = 9090       
SUBNET = "192.168.172"

# Servo specifications (from your working script)
MIN_PULSE = 500
MAX_PULSE = 2500
MAX_ANGLE = 280

# --- GPIO SETUP ---
pi = pigpio.pi()
if not pi.connected:
    print("Error: pigpiod daemon is not running! Run 'sudo pigpiod' first.")
    sys.exit(1)

def set_servo_angle(angle):
    """Converts degrees to pulse width and sends to servo."""
    try:
        val = float(angle)
        # Constrain between 0 and your maximum angle
        val = max(0, min(MAX_ANGLE, val))
        
        # Linear interpolation formula (from your working script)
        pulse = MIN_PULSE + (val / MAX_ANGLE) * (MAX_PULSE - MIN_PULSE)
        
        pi.set_servo_pulsewidth(SERVO_PIN, pulse)
        print(f"Angle {val}° -> Pulse {int(pulse)}µs")
        
    except Exception as e:
        print(f"Movement error: {e}")

def discover_pc_ip(subnet, port):
    """Scans the network for the Synnax server."""
    print(f"Scanning {subnet}.x for Synnax...")
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.01) 
                if s.connect_ex((ip, port)) == 0: 
                    return ip
        except: 
            continue
    return None

def main():
    pc_ip = discover_pc_ip(SUBNET, PORT)
    if not pc_ip:
        print("Error: Could not find PC. Make sure Synnax is running.")
        sys.exit(1)
        
    print(f"Connected to Synnax at {pc_ip}")

    try:
        # Authenticate and connect
        client = sy.Synnax(host=pc_ip, port=PORT, username="synnax", password="seldon", secure=False)
        chan = client.channels.retrieve("test_temperature")
        
        # --- ROBUST INITIAL SYNC ---
        print("Syncing with current state...")
        last_val = None
        initial_series = client.read_latest(chan)
        
        if initial_series is not None and len(initial_series) > 0:
            try:
                last_val = float(initial_series[0])
                print(f"System starting at existing value: {last_val}")
                # Optional: Tell it to move to this position immediately on startup
                # set_servo_angle(last_val)
            except Exception as e:
                print(f"Startup data error: {e}")
                last_val = None

        print("--- SYSTEM READY: Waiting for NEW commands ---")

        while True:
            latest_series = client.read_latest(chan)

            if latest_series is not None and len(latest_series) > 0:
                try:
                    current_val = float(latest_series[0])
                    
                    if last_val is None or current_val != last_val:
                        print(f"*** New Command Executing: {current_val} ***")
                        set_servo_angle(current_val)
                        last_val = current_val
                except Exception as e:
                    print(f"Loop data error: {e}")
            
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nScript stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"Run Error: {e}")
    finally:
        # Clean up pigpio connection on exit
        pi.set_servo_pulsewidth(SERVO_PIN, 0)
        pi.stop()
        print("pigpio Cleaned. Goodbye.")

if __name__ == "__main__":
    main()
