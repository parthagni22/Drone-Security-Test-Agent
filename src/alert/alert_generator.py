import json
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AlertGenerator:
    """Generates and manages security alerts."""
    
    def __init__(self):
        self.active_alerts = []
        self.alert_history = []
        self.notification_callbacks = []
    
    def generate_alert(self, alert_data):
        """
        Generate a new security alert.
        
        Args:
            alert_data: Dict containing alert information
            
        Returns:
            Dict: Generated alert with additional metadata
        """
        if not alert_data:
            return None
        
        # Add metadata to the alert
        enhanced_alert = {
            **alert_data,
            "alert_id": self._generate_alert_id(),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "active",
            "acknowledged": False
        }
        
        # Add to active alerts
        self.active_alerts.append(enhanced_alert)
        
        # Add to history
        self.alert_history.append(enhanced_alert)
        
        # Trigger notifications
        self._trigger_notifications(enhanced_alert)
        
        return enhanced_alert
    
    def acknowledge_alert(self, alert_id):
        """Mark an alert as acknowledged."""
        for alert in self.active_alerts:
            if alert.get("alert_id") == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
        return False
    
    def dismiss_alert(self, alert_id):
        """Dismiss an active alert."""
        for i, alert in enumerate(self.active_alerts):
            if alert.get("alert_id") == alert_id:
                alert["status"] = "dismissed"
                alert["dismissed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.active_alerts.pop(i)
                return True
        return False
    
    def get_active_alerts(self, priority=None):
        """Get currently active alerts, optionally filtered by priority."""
        if priority:
            return [alert for alert in self.active_alerts if alert.get("priority") == priority]
        return self.active_alerts.copy()
    
    def get_alert_history(self, limit=100):
        """Get alert history."""
        return self.alert_history[-limit:] if self.alert_history else []
    
    def add_notification_callback(self, callback):
        """Add a callback function to be called when alerts are generated."""
        if callable(callback):
            self.notification_callbacks.append(callback)
    
    def _generate_alert_id(self):
        """Generate a unique alert ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        import random
        suffix = random.randint(1000, 9999)
        return f"ALERT_{timestamp}_{suffix}"
    
    def _trigger_notifications(self, alert):
        """Trigger all registered notification callbacks."""
        for callback in self.notification_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Error in notification callback: {e}")
    
    def export_alerts(self, output_file):
        """Export all alerts to a JSON file."""
        data = {
            "active_alerts": self.active_alerts,
            "alert_history": self.alert_history,
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting alerts: {e}")
            return False
