import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data():
    """Generate sample energy consumption data"""
    np.random.seed(42)
    
    # Generate 30 days of hourly data
    start_date = datetime.now() - timedelta(days=30)
    dates = pd.date_range(start=start_date, periods=30*24, freq='H')
    
    data = []
    categories = ['Lighting', 'HVAC', 'Equipment', 'Other']
    devices = ['LED Lights', 'Air Conditioner', 'Computer', 'Refrigerator', 'Heater']
    locations = ['Office', 'Production Floor', 'Warehouse', 'Break Room']
    
    for i, timestamp in enumerate(dates):
        # Create realistic consumption patterns
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Base consumption with patterns
        if 6 <= hour <= 18:  # Daytime
            base_consumption = np.random.normal(5, 1.5)
        elif 18 <= hour <= 22:  # Evening
            base_consumption = np.random.normal(3, 1)
        else:  # Night
            base_consumption = np.random.normal(1, 0.5)
        
        # Weekend adjustment
        if day_of_week >= 5:  # Weekend
            base_consumption *= 0.7
        
        # Ensure positive values
        consumption = max(0.1, base_consumption)
        
        # Variable rate (peak hours cost more)
        if 16 <= hour <= 20:  # Peak hours
            rate = np.random.normal(0.18, 0.02)
        else:
            rate = np.random.normal(0.12, 0.01)
        
        rate = max(0.08, rate)  # Minimum rate
        
        data.append({
            'timestamp': timestamp,
            'consumption_kwh': round(consumption, 2),
            'rate_per_kwh': round(rate, 4),
            'cost': round(consumption * rate, 2),
            'category': np.random.choice(categories),
            'device': np.random.choice(devices),
            'location': np.random.choice(locations),
            'notes': f'Auto-generated data for {timestamp.strftime("%Y-%m-%d %H:%M")}'
        })
    
    return pd.DataFrame(data)