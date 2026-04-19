import RPi.GPIO as GPIO
import synnax as sy
import socket
import sys
import time

# --- CONFIG ---
SERVO_PIN = 18    
PORT = 9090       
SUBNET = "192.168.172"

# --- GPIO ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50) 
pwm.start(0) 

def set_servo_angle(angle):
    try:
        val = float(angle)
        # Duty cycle math: (angle / 18) + 2.5
        duty = (val / 18.0) + 2.5
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.3)
        pwm.ChangeDutyCycle(0)
    except:
        pass

def discover_pc_ip(subnet, port):
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.01) 
            if s.connect_ex((ip, port)) == 0: return ip
    return None

def main():
    pc_ip = discover_pc_ip(SUBNET, PORT)
    if not pc_ip:
        sys.exit(1)

    try:
        client = sy.Synnax(host=pc_ip, port=PORT, 
                           username="synnax", password="seldon", 
                           secure=False)
        print(f"Connected to {pc_ip}")

        chan = client.channels.retrieve("test_temperature")
        last_val = None

        print("--- READY: Use Synnax Console to send angles ---")

        while True:
            # read_latest returns a MultiSeries object
            latest_series = client.read_latest(chan)

            # Check if we actually got data back
            if latest_series is not None and len(latest_series) > 0:
                # Access the value by the channel name
                # We take [0] because it's the first (and only) row in the series
                current_val = latest_series[chan.name][0]
                
                if current_val != last_val:
                    print(f"New Command: {current_val}")
                    set_servo_angle(current_val)
                    last_val = current_val
            
            time.sleep(0.1)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        pwm.stop()
        GPIO.cleanup()
        print("GPIO Cleaned.")

if __name__ == "__main__":
    main()
