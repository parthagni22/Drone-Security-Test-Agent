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

```bash
python src/main.py --video path/to/your/video.mp4 --telemetry path/to/your/telemetry.json --output output_directory
```

Command line options:
- `--video`: Path to your video file (MP4, AVI, etc.)
- `--telemetry`: Path to your telemetry data (JSON format)
- `--output`: Directory to save processed frames and results
- `--frames`: Number of frames to process in simulation mode (default: 100)

### Simulated Mode

If no video file is provided, the system will run in simulation mode, generating fake video frames with text descriptions. This is useful for testing the system without actual video data.

## Frame Indexing and Querying

The system indexes all processed frames and detected objects in a SQLite database, allowing for efficient queries:

```python
# Query all frames containing trucks
truck_frames = frame_indexer.query_frames_by_object("truck")

# Query frames from a specific time range
morning_frames = frame_indexer.query_frames_by_time("06:00:00", "12:00:00")

# Query high-priority alerts
high_alerts = frame_indexer.query_alerts(priority="high")
```

## Alert Rules

The system comes with predefined alert rules that can be customized in `config.py`:

- **Person Loitering**: Triggers when a person is detected in the same location for over 60 seconds during nighttime hours
- **Vehicle in Restricted Area**: Alerts when vehicles are detected in designated restricted zones
- **Multiple People Gathering**: Notifies when groups of 3+ people gather during night hours

## Project Structure

```
drone_security_agent/
├── README.md
├── requirements.txt
├── data/
│   ├── sample_telemetry.json
│   └── sample_video.mp4
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_processor/
│   │   ├── __init__.py
│   │   ├── telemetry_processor.py
│   │   └── video_processor.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── object_detector.py
│   │   ├── context_analyzer.py
│   │   └── rule_engine.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── frame_indexer.py
│   │   └── event_logger.py
│   ├── alert/
│   │   ├── __init__.py
│   │   └── alert_generator.py
│   └── main.py
└── tests/
    ├── __init__.py
    └── test_drone_agent.py
```

## AI Tools Integration

This project was developed with assistance from AI tools to expedite the development process:

1. **Architecture Design**: Used Claude to brainstorm and refine the system architecture
2. **Code Generation**: Leveraged Claude to generate initial code structure and boilerplate
3. **Testing**: Used AI to help design test cases and validation scenarios

## Future Enhancements

Potential improvements for future versions:

1. **Real-time Video Processing**: Integration with real drone cameras through a streaming API
2. **Advanced Object Recognition**: Implement more sophisticated object detection using models like YOLOv8
3. **Geospatial Analysis**: Add GPS coordinates for mapping security events to physical locations
4. **Video Summarization**: Generate concise summaries of security events over specified time periods
5. **Mobile Notifications**: Send real-time alerts to property owners' mobile devices

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project was created as part of an AI Engineering assignment
- Sample data was generated for demonstration purposes only