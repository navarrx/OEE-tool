# OEE Calculator for R&D and Simulation Department

This application measures and tracks Overall Equipment Effectiveness (OEE) metrics for the R&D and Simulation Department, focusing on early fire detection models.

## Overview

The OEE Calculator helps track three key components:

- **Availability**: Measures system uptime and availability for simulations
- **Performance**: Compares actual simulation cycle time vs. ideal cycle time
- **Quality**: Tracks successful vs. failed simulations

The system allows you to record data, visualize trends, and generate reports to help improve simulation efficiency.

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

### GUI Dashboard

To run the application with the graphical user interface:

```
python oee_rd_simulation.py
```

or

```
python oee_rd_simulation.py gui
```

The GUI dashboard provides:
- Real-time OEE metrics
- Data input for simulation runs
- Historical data visualization
- Trend analysis

### Command Line Interface

The application also supports command-line operations:

**Calculate OEE metrics:**

```
python oee_rd_simulation.py calculate --model-name "Fire Detection Model" --planned-time 480 --downtime 60 --actual-cycle-time 15 --ideal-cycle-time 12 --total-simulations 100 --failed-simulations 10 --save
```

**Generate a report:**

```
python oee_rd_simulation.py report --model-name "Fire Detection Model" --days 30
```

**List recent simulations:**

```
python oee_rd_simulation.py list --model-name "all" --days 30
```

## Directory Structure

- `src/oee_rd_simulation/`: Main application code
  - `oee_calculator.py`: Core OEE calculation logic
  - `data_handler.py`: Data storage and retrieval
  - `gui.py`: GUI dashboard
  - `main.py`: Command-line interface and main entry point
- `data/`: Storage directory for simulation data (created on first run)

## OEE Formula

The Overall Equipment Effectiveness is calculated as:

```
OEE = Availability × Performance × Quality

Where:
- Availability = (Planned Time - Downtime) / Planned Time
- Performance = Ideal Cycle Time / Actual Cycle Time
- Quality = (Total Simulations - Failed Simulations) / Total Simulations
```

## Benchmarks

- World-class OEE: > 85%
- Typical OEE: 60-70%
- Low OEE: < 60% 