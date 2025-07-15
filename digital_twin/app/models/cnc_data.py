from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional

class CNCDataModel:
    def __init__(self, mongo_uri: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.cnc_database  # Adjust database name as needed
        self.collection = self.db.cutting_data  # Adjust collection name as needed
    
    def get_cutting_time_data(self, machine_id: str = None, 
                             start_date: datetime = None, 
                             end_date: datetime = None) -> List[Dict]:
        """Retrieve cutting time data from MongoDB"""
        query = {}
        
        if machine_id:
            query['machine_id'] = machine_id
        
        if start_date and end_date:
            query['timestamp'] = {
                '$gte': start_date,
                '$lte': end_date
            }
        
        cursor = self.collection.find(query).sort('timestamp', -1)
        return list(cursor)
    
    def get_machine_status(self, machine_id: str) -> Dict:
        """Get current machine status"""
        latest_data = self.collection.find_one(
            {'machine_id': machine_id},
            sort=[('timestamp', -1)]
        )
        
        if not latest_data:
            return {'status': 'offline', 'last_seen': None}
        
        # Check if machine is active (last data within 5 minutes)
        time_diff = datetime.now() - latest_data['timestamp']
        is_active = time_diff < timedelta(minutes=5)
        
        return {
            'status': 'active' if is_active else 'idle',
            'last_seen': latest_data['timestamp'],
            'current_cutting_time': latest_data.get('cutting_time', 0),
            'spindle_speed': latest_data.get('spindle_speed', 0),
            'feed_rate': latest_data.get('feed_rate', 0)
        }
    
    def get_performance_metrics(self, machine_id: str, hours: int = 24) -> Dict:
        """Calculate performance metrics for the digital twin"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        data = self.get_cutting_time_data(machine_id, start_time, end_time)
        
        if not data:
            return {'error': 'No data available'}
        
        df = pd.DataFrame(data)
        
        metrics = {
            'total_cutting_time': df['cutting_time'].sum(),
            'average_cutting_time': df['cutting_time'].mean(),
            'max_cutting_time': df['cutting_time'].max(),
            'min_cutting_time': df['cutting_time'].min(),
            'total_operations': len(df),
            'efficiency': self._calculate_efficiency(df),
            'utilization': self._calculate_utilization(df, hours)
        }
        
        return metrics
    
    def _calculate_efficiency(self, df: pd.DataFrame) -> float:
        """Calculate machine efficiency based on cutting time data"""
        if df.empty:
            return 0.0
        
        # Efficiency = (Actual cutting time / Planned cutting time) * 100
        # For now, we'll use a simple metric based on consistency
        std_dev = df['cutting_time'].std()
        mean_time = df['cutting_time'].mean()
        
        if mean_time == 0:
            return 0.0
        
        coefficient_of_variation = std_dev / mean_time
        efficiency = max(0, 100 - (coefficient_of_variation * 100))
        
        return round(efficiency, 2)
    
    def _calculate_utilization(self, df: pd.DataFrame, hours: int) -> float:
        """Calculate machine utilization"""
        if df.empty:
            return 0.0
        
        total_cutting_time = df['cutting_time'].sum()
        total_available_time = hours * 3600  # Convert to seconds
        
        utilization = (total_cutting_time / total_available_time) * 100
        return round(min(utilization, 100), 2)
    
    def insert_cutting_data(self, data: Dict) -> str:
        """Insert new cutting data"""
        data['timestamp'] = datetime.now()
        result = self.collection.insert_one(data)
        return str(result.inserted_id)