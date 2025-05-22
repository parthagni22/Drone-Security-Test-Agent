# Drone Security Analyst Agent

A prototype system for monitoring property security using drone-captured video and telemetry data. The system identifies objects, generates alerts, and provides queryable security event history.

## Value Proposition

The Drone Security Analyst Agent enhances property security through automated 24/7 monitoring, intelligent object recognition, and proactive alert generation, reducing the need for constant human surveillance while improving incident detection and response times.

## Key Features

- **Real-time Object Recognition**: Identify and classify objects including vehicles, people, and animals with contextual information (time, location)
- **Intelligent Alert System**: Generate customizable security alerts based on predefined rules (unauthorized entry, loitering, unusual activity)
- **Searchable Security Archive**: Query historical security events by object type, time, or location

## System Architecture

![System Architecture](docs/architecture.png)

The system consists of the following components:

1. **Data Ingestion Layer**:
   - Video Frame Processor: Extracts frames from video feed
   - Telemetry Data Processor: Parses drone position, altitude, etc.

2. **Analysis Layer**:
   - Object Detection Module: Identifies objects in frames
   - Context Analyzer: Correlates objects with telemetry data
   - Rule Engine: Evaluates security rules against detected objects/events

3. **Storage Layer**:
   - Frame Index Database: Stores processed frames with metadata
   - Event Log: Records all detected objects and security events

4. **Alert System**:
   - Alert Generator: Creates alerts based on rule violations
   - Notification Service: Delivers alerts to the user interface

5. **Query Interface**:
   - Search Engine: Allows querying the frame index by time, object, or location

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/drone-security-agent.git
   cd drone-security-agent
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Simulation

To run the drone security system with default settings:

```bash
python src/main.py
```

This will process the sample video and telemetry data included in the `data` directory.

### Custom Settings

You can specify your own video source and telemetry data: