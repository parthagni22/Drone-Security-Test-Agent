# Telemetry data processor

import json
from datetime import datetime

class TelemetryProcessor:
    def __init__(self, telemetry_file=None):
        self.telemetry_data = []
        if telemetry_file:
            self.load_telemetry(telemetry_file)
    
    def load_telemetry(self, telemetry_file):
        """Load telemetry data from a JSON file."""
        try:
            with open(telemetry_file, 'r') as f:
                self.telemetry_data = json.load(f)
            print(f"Loaded {len(self.telemetry_data)} telemetry records")
        except Exception as e:
            print(f"Error loading telemetry data: {e}")
            # Create sample data if file doesn't exist
            self.generate_sample_telemetry()
    
    def generate_sample_telemetry(self, num_records=100):
        """Generate sample telemetry data."""
        import random
        from datetime import datetime, timedelta
        
        self.telemetry_data = []
        locations = ["Gate", "Garage", "Backyard", "Perimeter", "Main Entrance"]
        start_time = datetime.now()
        
        for i in range(num_records):
            timestamp = (start_time + timedelta(seconds=i*5)).strftime("%H:%M:%S")
            self.telemetry_data.append({
                "timestamp": timestamp,
                "location": random.choice(locations),
                "altitude": round(random.uniform(2.0, 10.0), 2),
                "battery": random.randint(50, 100),
                "status": "monitoring"
            })
        
        print(f"Generated {len(self.telemetry_data)} sample telemetry records")
    
    def get_telemetry_at_time(self, timestamp):
        """Get telemetry data closest to the given timestamp."""
        if not self.telemetry_data:
            return None
        
        # Convert timestamp string to datetime for comparison
        if isinstance(timestamp, str):
            try:
                target_time = datetime.strptime(timestamp, "%H:%M:%S")
            except ValueError:
                print(f"Invalid timestamp format: {timestamp}")
                return None
        else:
            target_time = timestamp
        
        # Find closest telemetry entry
        closest_entry = None
        min_diff = float('inf')
        
        for entry in self.telemetry_data:
            entry_time = datetime.strptime(entry["timestamp"], "%H:%M:%S")
            time_diff = abs((target_time - entry_time).total_seconds())
            
            if time_diff < min_diff:
                min_diff = time_diff
                closest_entry = entry
        
        return closest_entry
    
    def save_telemetry(self, output_file):
        """Save telemetry data to a JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.telemetry_data, f, indent=2)
            print(f"Saved telemetry data to {output_file}")
        except Exception as e:
            print(f"Error saving telemetry data: {e}")
