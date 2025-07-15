import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime, timedelta

class EnergyForecasting:
    def __init__(self, data):
        self.data = data
    
    def show_forecasting_interface(self):
        st.subheader("Energy Consumption Forecasting")
        
        # Forecasting parameters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            forecast_days = st.number_input("Forecast Days", min_value=1, max_value=365, value=30)
        
        with col2:
            model_type = st.selectbox("Model Type", ["Linear Regression", "Polynomial Regression", "Moving Average"])
        
        with col3:
            confidence_interval = st.slider("Confidence Interval", 0.8, 0.99, 0.95)
        
        if st.button("Generate Forecast"):
            with st.spinner("Generating forecast..."):
                forecast_data = self.generate_forecast(forecast_days, model_type)
                self.display_forecast(forecast_data, model_type)
    
    def generate_forecast(self, days, model_type):
        # Prepare data for forecasting
        daily_data = self.data.groupby(self.data['timestamp'].dt.date)['consumption_kwh'].sum().reset_index()
        daily_data.columns = ['date', 'consumption']
        daily_data['date'] = pd.to_datetime(daily_data['date'])
        daily_data = daily_data.sort_values('date')
        
        # Create features
        daily_data['day_num'] = range(len(daily_data))
        
        X = daily_data[['day_num']].values
        y = daily_data['consumption'].values
        
        if model_type == "Linear Regression":
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate future dates
            future_days = np.arange(len(daily_data), len(daily_data) + days).reshape(-1, 1)
            predictions = model.predict(future_days)
            
        elif model_type == "Polynomial Regression":
            poly_features = PolynomialFeatures(degree=2)
            X_poly = poly_features.fit_transform(X)
            
            model = LinearRegression()
            model.fit(X_poly, y)
            
            future_days = np.arange(len(daily_data), len(daily_data) + days).reshape(-1, 1)
            future_days_poly = poly_features.transform(future_days)
            predictions = model.predict(future_days_poly)
            
        elif model_type == "Moving Average":
            window = min(7, len(daily_data))
            moving_avg = daily_data['consumption'].rolling(window=window).mean().iloc[-1]
            predictions = np.full(days, moving_avg)
        
        # Create forecast dataframe
        last_date = daily_data['date'].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days, freq='D')
        
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_consumption': np.maximum(predictions, 0),  # Ensure non-negative
            'model_type': model_type
        })
        
        return forecast_df
    
    def display_forecast(self, forecast_data, model_type):
        st.subheader(f"Forecast Results - {model_type}")
        
        # Historical data
        historical_daily = self.data.groupby(self.data['timestamp'].dt.date)['consumption_kwh'].sum().reset_index()
        historical_daily.columns = ['date', 'consumption']
        
        # Create combined plot
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=historical_daily['date'],
            y=historical_daily['consumption'],
            mode='lines',
            name='Historical',
            line=dict(color='blue')
        ))
        
        # Forecast data
        fig.add_trace(go.Scatter(
            x=forecast_data['date'],
            y=forecast_data['predicted_consumption'],
            mode='lines',
            name='Forecast',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title="Energy Consumption Forecast",
            xaxis_title="Date",
            yaxis_title="Consumption (kWh)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast summary
        st.subheader("Forecast Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_forecast = forecast_data['predicted_consumption'].mean()
            st.metric("Avg Daily Forecast", f"{avg_forecast:.2f} kWh")
        
        with col2:
            total_forecast = forecast_data['predicted_consumption'].sum()
            st.metric("Total Forecast", f"{total_forecast:.2f} kWh")
        
        with col3:
            historical_avg = historical_daily['consumption'].mean()
            change = ((avg_forecast - historical_avg) / historical_avg) * 100
            st.metric("Change from Historical", f"{change:+.1f}%")
        
        # Display forecast table
        st.subheader("Detailed Forecast")
        st.dataframe(forecast_data)