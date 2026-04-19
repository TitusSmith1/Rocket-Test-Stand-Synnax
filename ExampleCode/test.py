import synnax as sy
import socket
import sys
import time
import random

# --- CONFIGURATION ---
PORT = 9090
SUBNET = "192.168.172"
TICK_RATE = 0.1  # Seconds between loop iterations (10 Hz)

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

def main():
    pc_ip = discover_pc_ip(SUBNET, PORT)
    if not pc_ip:
        print("Error: Could not find PC. Make sure Synnax is running.")
        sys.exit(1)

    print(f"Connected to Synnax at {pc_ip}")

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

        writer = client.open_writer(
            start=sy.TimeStamp.now(),
            channels=["time", "valve_1_state", "valve_2_state", "valve_3_state", "pt_1", "pt_2", "pt_3", "load_cell_1"],
            mode="persist_stream",
        )

        #reader = client.open_streamer("valve_1_cmd","valve_2_cmd","valve_3_cmd")
        
        # --- 3. MAIN LOOP ---
        while True:
            now = sy.TimeStamp.now()

            # A. Read Commands
            for i in range(3):
                latest_cmd = client.read_latest([valve_cmds[i]],1)
                #print(latest_cmd)
                #if latest_cmd is not None and len(latest_cmd) > 0:
                #    current_valve_states[i] = int(latest_cmd[0])

            # B. Generate Simulated Sensor Data
            # Let's add a little "physics": If a valve is open (1), pressure drops.
            simulated_pts = []
            for i in range(3):
                base_pressure = 100.0 if current_valve_states[i] == 1 else 500.0
                noise = random.uniform(-2.5, 2.5) # +/- 2.5 psi noise
                simulated_pts.append(base_pressure + noise)

            # Load cell hovers around 1500 lbf with some noise
            simulated_load = 1500.0 + random.uniform(-10.0, 10.0)

            # C. Write Data to Synnax
            # We bundle the writes into a list of Series to push them all at the current timestamp
            
            # Write valve states
            """
            for i in range(3):
                write_data.append(sy.Series(valve_states[i], data=[current_valve_states[i]], timestamps=[now]))
            
            # Write PTs
            for i in range(3):
                write_data.append(sy.Series(pt_chans[i], data=[simulated_pts[i]], timestamps=[now]))
            
            # Write Load Cell
            write_data.append(sy.Series(load_cell_chan, data=[simulated_load], timestamps=[now]))

            """
            
            """
            # Write valve states
            for i in range(3):
                write_data.append(sy.Series(
                    channel=valve_states[i], 
                    data=[current_valve_states[i]], 
                    timestamps=[now]
                ))
            
            # Write PTs
            for i in range(3):
                write_data.append(sy.Series(
                    channel=pt_chans[i], 
                    data=[simulated_pts[i]], 
                    timestamps=[now]
                ))
                
            
            # Write Load Cell
            write_data.append(sy.Series(
                channel=load_cell_chan, 
                data=[simulated_load], 
                timestamps=[now]
            ))
            """

            writer.write(["time", "valve_1_state", "valve_2_state", "valve_3_state", "pt_1", "pt_2", "pt_3", "load_cell_1"],
             [
                now, current_valve_states[0], current_valve_states[1], current_valve_states[2], simulated_pts[0], simulated_pts[1], simulated_pts[2], simulated_load
            ])

            # Execute the write
            #client.write(write_data)

            # Print status to terminal occasionally so you know it's alive
            print(f"[{now}] V1: {current_valve_states[0]} | PT1: {simulated_pts[0]:.1f} psi | Load: {simulated_load:.1f} lbf", end="\r")

            time.sleep(TICK_RATE)


    except KeyboardInterrupt:
        print("\nEmulator stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"\nRun Error: {e}")

if __name__ == "__main__":
    main()
