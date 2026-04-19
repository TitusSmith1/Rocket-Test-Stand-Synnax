
#  Copyright 2026 Synnax Labs, Inc.
#
#  Use of this software is governed by the Business Source License included in the file
#  licenses/BSL.txt.
#
#  As of the Change Date specified in that file, in accordance with the Business Source
#  License, use of this software will be governed by the Apache License, Version 2.0,
#  included in the file licenses/APL.txt.

"""
This example demonstrates streaming data from a large number of channels into Synnax,
while also acknowledging commands sent to a large number of simulated valves. This
example serves as a basic simulated data acquisition system (DAQ). While this example is
running, you could open a schematic in the Synnax Console to control valves and view
sensors.
"""

import numpy as np
import sys
import socket
import synnax as sy
import "SensorCode/thermo.py" as thermo
import "SensorCode/igniter.py" as igniter
import "SensorCode/pt.py" as pt
import "SensorCode/servo.py" as servo

# --- CONFIGURATION ---
PORT = 9090
SUBNET = "192.168.172"

NUM_VALVES = 3
NUM_SENSORS = 5
sensor_names = ["PT1","PT2","PT3","Load_Cell","TC"] # PT = Pressure Transducer, TC = Thermocouple
valve_names = ["Valve_1","Valve_2","Valve_3"] 

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
    #start host discovery
    pc_ip = discover_pc_ip(SUBNET, PORT)
    if not pc_ip:
        print("Error: Could not find PC. Make sure Synnax is running.")
        sys.exit(1)

    print(f"Connected to Synnax at {pc_ip}")

    client = sy.Synnax(host=pc_ip, port=PORT, username="teststand", password="teststand", secure=False)

    # Some lists to store our channels.
    valve_commands = list()
    valve_responses = list()

    # Maps the keys of valve command channels to response channels.
    command_to_response = {}

    # Stores the timestamps for both the sensors and the valve responses.
    sensor_time_channel = client.channels.create(
        name="time",
        is_index=True,
        data_type=sy.DataType.TIMESTAMP,
        retrieve_if_name_exists=True,
    )

    # Create the necessary channels for each valve.
    for i in range(NUM_VALVES):
        # The index channel for the command is used to track the time at which the command
        # was sent. We need to have separate indexes for each command channel so that these
        # channels can be written to independently.
        cmd_index_channel = client.channels.create(
            name=valve_names[i]+"_command_time",
            is_index=True,
            data_type=sy.DataType.TIMESTAMP,
            retrieve_if_name_exists=True,
        )
        cmd_res = client.channels.create(
            [
                # The command channel is used to send a command to the valve.
                sy.Channel(
                    name=valve_names[i]+"_command",
                    index=cmd_index_channel.key,
                    data_type=sy.DataType.UINT8,
                ),
                # The response channel is used to acknowledge the response from our simulated
                # DAQ.
                sy.Channel(
                    name=valve_names[i]+"_response",
                    index=sensor_time_channel.key,
                    data_type=sy.DataType.UINT8,
                ),
            ],
            retrieve_if_name_exists=True,
        )
        cmd = cmd_res[0]
        res = cmd_res[1]
        valve_commands.append(cmd)
        valve_responses.append(res)
        command_to_response[cmd.key] = res

    # Defining the sensor channels to create.
    sensors = [
        sy.Channel(
            name=sensor_names[i],
            index=sensor_time_channel.key,
            data_type=sy.DataType.FLOAT32,
        )
        for i in range(NUM_SENSORS)
    ]

    # Actually creating the sensor channels on the Synnax cluster.
    sensors = client.channels.create(sensors, retrieve_if_name_exists=True)

    # Define the list of channels we'll write to (the sensor channels and the valve
    # responses)
    write_to = [
        sensor_time_channel.key,  # sensor time
        *[s.key for s in sensors],  # sensor data
        *[v.key for v in valve_responses],  # valve responses
    ]

    # Define the list of channels we'll read from (the incoming valve commands)
    read_from = [v.key for v in valve_commands]

    # Define a rate at which we'll write data.
    loop = sy.Loop(sy.Rate.HZ * 100)

    # Set up the initial state of the valves to 0x00 (closed).
    sensor_states = {v.key: np.uint8(False) for v in valve_responses}

    # Open a streamer to listen for incoming valve commands.
    with client.open_streamer([channel.key for channel in valve_commands]) as streamer:
        i = 0
        # Open a writer to write data to Synnax.
        with client.open_writer(sy.TimeStamp.now(), write_to) as writer:
            start = sy.TimeStamp.now()
            while loop.wait():  # run this loop at the defined rate of 100 Hz
                # If we've received a command, update the state of the corresponding valve.
                frame = streamer.read(timeout=0)    #read any incoming valve commands, but don't wait if there are none (timeout=0)
                if frame is not None:   #if we've received a command, update the state of the corresponding valve
                    for channel_key in frame.channels:
                        # 1 is open, 0 is closed
                        #if the command channel has a value greater than 0.9, we consider the valve to be open (1), otherwise it's closed (0). 
                        # We write this state to the corresponding response channel.
                        valve_response_channel = command_to_response[channel_key]
                        valve_command = frame[channel_key][-1]  # get the most recent command for this channel
                        sensor_states[valve_response_channel.key] = np.uint8(valve_command > 0.9)   #write back the response to the valve opening/closing

                        if channel_key == "Valve_1_command":
                            if valve_command > 0.9:
                                print("Opening Valve 1")
                        elif channel_key == "Valve_2_command":
                            if valve_command > 0.9:
                                print("Opening Valve 2")
                        elif channel_key == "Valve_3_command":
                            if valve_command > 0.9:
                                print("Opening Valve 3")

                #handle writing sensor data. 
                for j, channel in enumerate(sensors):
                    #write sine wave to sensor channels shifted by the sensor index. 
                    sensor_states[channel.key] = np.float32(np.sin(i / 1000) + j / 100) # change this to write to sensor channel
                    #if channel.key == "PT1":
                    #    sensor_states[channel.key] = np.float32(100 + 10 * np.sin(i / 1000))
                    #elif channel.key == "PT2":
                    #    sensor_states[channel.key] = np.float32(150 + 15 * np.cos(i / 1000))
                    #elif channel.key == "PT3":
                    #    sensor_states[channel.key] = np.float32(200 + 20 * np.sin(i / 500))
                    #elif channel.key == "Load_Cell":
                    #    sensor_states[channel.key] = np.float32(50 + 5 * np.sin(i / 2000))
                    #elif channel.key == "TC":
                    #    sensor_states[channel.key] = np.float32(25 + 10 * np.cos(i / 1500))

                sensor_states[sensor_time_channel.key] = sy.TimeStamp.now()
                writer.write(sensor_states)
                i += 1

if __name__=="__main__":
    main()