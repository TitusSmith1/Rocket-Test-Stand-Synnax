import time
import random
import math
from synnax import Synnax
import threading
stop = threading.Event()


# Configuration
PORT = 9090
SUBNET = "192.168.0"#  .172"

client = None

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

def get_or_create_channel(client, name, data_type, index_chan=None):
    """Safely retrieves an existing channel or creates a new one."""
    try:
        return client.channels.retrieve(name)
    except Exception:
        # If it doesn't exist, create it
        if index_chan is None:
            return client.channels.create(name=name, data_type=data_type, is_index=True)
        else:
            return client.channels.create(name=name, data_type=data_type, index=index_chan.key)

def run_test_stand():
    client = Synnax(address=CORE_ADDRESS)
    
    # --- Channel Initialization ---
    # Define your hardware map
    channels = {
        "p_tank":  client.channels.get_or_create("Pressure_Tank", unit="PSI"),
        "p_feed":  client.channels.get_or_create("Pressure_Feed", unit="PSI"),
        "p_cham":  client.channels.get_or_create("Pressure_Chamber", unit="PSI"),
        "v_main":  client.channels.get_or_create("Valve_Main", unit="POS"),
        "v_vent":  client.channels.get_or_create("Valve_Vent", unit="POS"),
        "v_purge": client.channels.get_or_create("Valve_Purge", unit="POS"),
        "thrust":  client.channels.get_or_create("Load_Cell_Thrust", unit="N"),
    }

    print("Emulation active. Press Ctrl+C to stop.")
    
    start_time = time.time()
    try:
        while True:
            now = time.time()
            elapsed = now - start_time
            ts = int(now * 1e9) # Nanosecond timestamp

            # --- Data Emulation Logic ---
            # Pressure: Slight decay over time
            p_val = max(0, 500 - (elapsed * 0.5) + random.uniform(-1, 1))
            # Thrust: Only shows value if "Main Valve" is "open"
            thrust_val = 1500 + random.uniform(-10, 10) if elapsed > 5 else 0
            # Valve: Binary or percentage st
            v_pos = 100 if elapsed > 5 else 0

            # --- Synnax Write Operation ---
            client.write({
                channels["p_tank"]:  [(ts, p_val)],
                channels["p_feed"]:  [(ts, p_val * 0.95)],
                channels["p_cham"]:  [(ts, p_val * 0.1)],
                channels["v_main"]:  [(ts, v_pos)],
                channels["v_vent"]:  [(ts, 0)],
                channels["v_purge"]: [(ts, 0)],
                channels["thrust"]:  [(ts, thrust_val)],
            })

            time.sleep(1 / RATE_HZ)

    except KeyboardInterrupt:
        print("\nShutting down safely.")

def handle_setup():
    IP = discover_pc_ip(SUBNET, PORT)
    if not IP:
        print("Error: Could not find Synnax server. Make sure it's running and on the same network.")
        return True
    print(f"Connected to Synnax at {IP}")

    try:
        # Authenticate and connect
        client = sy.Synnax(host=pc_ip, port=PORT, username="synnax", password="seldon", secure=False)
        
        # --- 1. SETUP CHANNELS ---
        print("Setting up telemetry channels...")
        time_chan = get_or_create_channel(client, "time", sy.DataType.TIMESTAMP)

        # Valve Channels (Commands to read, States to write)
        valve_cmds = []
        valve_states = []
        for i in range(1, 4):
            # INT8 is great for binary 0/1 state
            valve_cmds.append(get_or_create_channel(client, f"valve_{i}_cmd", sy.DataType.INT8, time_chan))
            valve_states.append(get_or_create_channel(client, f"valve_{i}_state", sy.DataType.INT8, time_chan))

        # Sensor Channels (FLOAT32)
        pt_chans = []
        for i in range(1, 4):
            pt_chans.append(get_or_create_channel(client, f"pt_{i}", sy.DataType.FLOAT32, time_chan))
        
        load_cell_chan = get_or_create_channel(client, "load_cell_1", sy.DataType.FLOAT32, time_chan)

        # --- 2. INITIALIZE EMULATOR STATE ---
        # Keep track of our virtual hardware state
        current_valve_states = [0, 0, 0] 

        print("--- TEST STAND EMULATOR RUNNING ---")
        print("Waiting for commands and broadcasting telemetry. Press Ctrl+C to stop.")
    except Exception as e:
        print(f"\nRun Error: {e}")
    return False


#thread to handle valve control
def run_test_stand():
    while not stop.isSet():
        #do valve handling
        sleep(5)
    if stop.isSet():
        print("KeyboardInterrupt detected, closing test stand thread. ")

#thread to monitor sensors
def monitor_sensors():
    while not stop.isSet():
        #monitor sensors
        sleep(5)
    if stop.isSet():
        print("KeyboardInterrupt detected, closing monitoring thread. ")

#thread to handle synnax comms
def stream_data():
    while not stop.isSet():
        #synnax streaming
    if stop.isSet():
        print("KeyboardInterrupt detected, closing streaming thread. ")


#main function for initialization
def main(argv):
    #handle setup
    if(handle_setup()):
        return 1

    #create threads for sensor polling and data streaming and monitoring
    control_thread = threading.Thread(target=run_test_stand)
    sensor_thread = threading.Thread(target=monitor_sensors)
    stream_thread = threading.Thread(target=stream_data)

    #start the threads
    sensor_thread.start()
    control_thread.start()
    stream_thread.start()

    try:
        print("Waiting for background threads to finish")
        while sensor_thread.is_alive() or control_thread.is_alive() or stream_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        stop.set()
        print("Closing main-thread.Please wait for background thread to finish the current item.")
        return 0
    sensor_thread.join()
    control_thread.join()
    stream_thread.join()
    print("Thread finished all tasks, exiting")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))