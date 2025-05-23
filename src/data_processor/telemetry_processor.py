import json
from datetime import datetime
import random

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
            self.generate_sample_telemetry()
    
    def generate_sample_telemetry(self, num_records=100):
        """Generate realistic telemetry data based on detection context."""
        import random
        from datetime import datetime, timedelta
        
        self.telemetry_data = []
        
        # More realistic locations for different scenarios
        locations = [
            "Highway_Overpass", "Main_Road", "Traffic_Junction", 
            "Parking_Area", "Building_Entrance", "Perimeter_Fence",
            "Vehicle_Access_Point", "Public_Road", "Security_Zone"
        ]
        
        start_time = datetime.now()
        
        for i in range(num_records):
            timestamp = (start_time + timedelta(seconds=i*2)).strftime("%H:%M:%S")
            
            # Vary location based on time for realism
            if i < num_records // 3:
                location = "Highway_Overpass"
            elif i < 2 * num_records // 3:
                location = "Main_Road"
            else:
                location = random.choice(locations)
            
            self.telemetry_data.append({
                "timestamp": timestamp,
                "location": location,
                "altitude": round(random.uniform(10.0, 50.0), 2),  # Higher for drone footage
                "battery": random.randint(70, 100),
                "status": "monitoring"
            })
        
        print(f"Generated {len(self.telemetry_data)} telemetry records with realistic locations")
    
    def get_telemetry_at_time(self, timestamp):
        """Get telemetry data closest to the given timestamp."""
        if not self.telemetry_data:
            return {
                "location": "Highway_Overpass",
                "altitude": 25.0,
                "battery": 85,
                "status": "monitoring"
            }
        
        # Find closest telemetry entry
        try:
            target_time = datetime.strptime(timestamp, "%H:%M:%S")
        except ValueError:
            return self.telemetry_data[0] if self.telemetry_data else {}
        
        closest_entry = None
        min_diff = float('inf')
        
        for entry in self.telemetry_data:
            try:
                entry_time = datetime.strptime(entry["timestamp"], "%H:%M:%S")
                time_diff = abs((target_time - entry_time).total_seconds())
                
                if time_diff < min_diff:
                    min_diff = time_diff
                    closest_entry = entry
            except:
                continue
        
        return closest_entry if closest_entry else self.telemetry_data[0]
    
    def save_telemetry(self, output_file):
        """Save telemetry data to a JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.telemetry_data, f, indent=2)
            print(f"Saved telemetry data to {output_file}")
        except Exception as e:
            print(f"Error saving telemetry data: {e}")
