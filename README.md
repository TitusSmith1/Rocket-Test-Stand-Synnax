# Synnax Code

A rocket engine test stand simulation using Synnax for data acquisition and control.

## Overview

This project demonstrates a simulated data acquisition system (DAQ) that:
- Streams data from multiple sensors (pressure transducers, thermocouples, load cells)
- Acknowledges commands sent to simulated valves
- Integrates with Synnax Console for visualization and control

## Project Structure

```
SynnaxTest2/
├── simulation.py          # Main DAQ simulation script
├── Dashboard/
│   └── P&ID.json         # P&ID schematic for Synnax Console
└── ExampleCode/
    ├── sampledata.py     # Sample data handling code
    └── test.py           # Test scripts
```

## Requirements

- Python 3.8+
- Synnax Python client
- NumPy

Install dependencies:
```bash
pip install synnax numpy
```

## Running the Simulation

1. Start the Synnax server
2. Run the simulation:
```bash
python simulation.py
```

The script will:
- Discover the Synnax server on the network
- Create channels for sensors and valves
- Stream simulated sensor data
- Listen for valve commands from Synnax Console

## Configuration

Edit the configuration section in `simulation.py`:
- `PORT` - Synnax server port (default: 9090)
- `SUBNET` - Network subnet to scan
- `NUM_VALVES` - Number of simulated valves
- `NUM_SENSORS` - Number of simulated sensors

## Dashboard

The `Dashboard/P&ID.json` contains a P&ID schematic for a rocket engine test stand with:
- Nitrogen and Oxygen tanks
- Ethanol fuel tank
- Pressure regulators
- Ball valves
- Pressure transducers (PT1, PT2, PT3)
- Thermocouple (TC)
- Load cell
- Igniter

Load this file in Synnax Console to visualize and control the simulation.

## License

Copyright 2026 Synnax Labs, Inc. See `licenses/BSL.txt` for license details.
