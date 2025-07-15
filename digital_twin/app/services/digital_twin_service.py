import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import json

class DigitalTwinService:
    def __init__(self, cnc_model):
        self.cnc_model = cnc_model
        self.prediction_models = {}
    
    def get_twin_state(self, machine_id: str) -> Dict:
        """Get the current state of the digital twin"""
        # Get real-time data
        status = self.cnc_model.get_machine_status(machine_id)
        metrics = self.cnc_model.get_performance_metrics(machine_id)
        
        # Get recent cutting data for visualization
        recent_data = self.cnc_model.get_cutting_time_data(
            machine_id, 
            datetime.now() - timedelta(hours=24)
        )
        
        # Prepare time series data for charts
        time_series = self._prepare_time_series(recent_data)
        
        # Predict next maintenance
        maintenance_prediction = self._predict_maintenance(machine_id)
        
        # Calculate anomalies
        anomalies = self._detect_anomalies(recent_data)
        
        return {
            'machine_id': machine_id,
            'status': status,
            'metrics': metrics,
            'time_series': time_series,
            'maintenance_prediction': maintenance_prediction,
            'anomalies': anomalies,
            'last_updated': datetime.now().isoformat()
        }
    
    def _prepare_time_series(self, data: List[Dict]) -> Dict:
        """Prepare time series data for visualization"""
        if not data:
            return {'timestamps': [], 'cutting_times': [], 'spindle_speeds': []}
        
        timestamps = [item['timestamp'].isoformat() for item in data]
        cutting_times = [item.get('cutting_time', 0) for item in data]
        spindle_speeds = [item.get('spindle_speed', 0) for item in data]
        feed_rates = [item.get('feed_rate', 0) for item in data]
        
        return {
            'timestamps': timestamps,
            'cutting_times': cutting_times,
            'spindle_speeds': spindle_speeds,
            'feed_rates': feed_rates
        }
    
    def _predict_maintenance(self, machine_id: str) -> Dict:
        """Simple maintenance prediction based on cutting time patterns"""
        # Get data from last 7 days
        data = self.cnc_model.get_cutting_time_data(
            machine_id,
            datetime.now() - timedelta(days=7)
        )
        
        if len(data) < 10:
            return {'prediction': 'Insufficient data', 'confidence': 0}
        
        cutting_times = [item.get('cutting_time', 0) for item in data]
        
        # Simple trend analysis
        recent_avg = np.mean(cutting_times[-10:])
        overall_avg = np.mean(cutting_times)
        
        if recent_avg > overall_avg * 1.2:
            return {
                'prediction': 'Maintenance recommended within 3 days',
                'confidence': 75,
                'reason': 'Cutting times increasing above normal'
            }
        elif recent_avg < overall_avg * 0.8:
            return {
                'prediction': 'Tool wear detected',
                'confidence': 60,
                'reason': 'Cutting times decreasing significantly'
            }
        else:
            return {
                'prediction': 'Normal operation',
                'confidence': 80,
                'reason': 'Cutting times within normal range'
            }
    
    def _detect_anomalies(self, data: List[Dict]) -> List[Dict]:
        """Detect anomalies in cutting time data"""
        if len(data) < 20:
            return []
        
        cutting_times = [item.get('cutting_time', 0) for item in data]
        
        # Calculate z-scores
        mean_time = np.mean(cutting_times)
        std_time = np.std(cutting_times)
        
        anomalies = []
        for i, item in enumerate(data):
            cutting_time = item.get('cutting_time', 0)
            z_score = abs((cutting_time - mean_time) / std_time) if std_time > 0 else 0
            
            if z_score > 2:  # Threshold for anomaly
                anomalies.append({
                    'timestamp': item['timestamp'].isoformat(),
                    'cutting_time': cutting_time,
                    'z_score': round(z_score, 2),
                    'type': 'high' if cutting_time > mean_time else 'low'
                })
        
        return anomalies[-10:]  # Return last 10 anomalies