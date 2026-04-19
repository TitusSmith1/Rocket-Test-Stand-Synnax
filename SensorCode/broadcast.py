import time
import synnax as sy

# --- CONFIGURATION ---
HOST = "192.168.172.56" 
PORT = 9090
# Ensure these match exactly what you created earlier
CHANNELS = ["time", "pressure_1", "pressure_2", "temp_main"]

def main():
    print(f"Connecting to Synnax at {HOST}...")
    try:
        client = sy.Synnax(host=HOST, port=PORT, username="synnax", password="seldon", secure=False)
        print("Connected successfully!")
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    print("Opening Synnax writer...")
    try:
        # 1. By setting start to sy.TimeStamp.now(), we anchor to the exact present.
        # 2. We use 'with' so the writer closes safely if there's an error.
        with client.open_writer(channels=CHANNELS, start=sy.TimeStamp.now()) as writer:
            print("Stream active. Sending telemetry (Ctrl+C to stop).")
            
            while True:
                # Get fresh time
                now = sy.TimeStamp.now()
                
                # Write the data
                writer.write({
                    "time": now,
                    "pressure_1": 14.7,
                    "pressure_2": 15.2,
                    "temp_main": 72.5
                })
                
                print(f"Uploaded: {now}", end="\r")
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        # If we see "time range not found" here, it's a server-side index issue
        print(f"\nBroadcast Error: {e}")

if __name__ == "__main__":
    main()
