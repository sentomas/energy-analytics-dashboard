import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class EnergyAnalytics:
    def __init__(self, data):
        self.data = data
    
    def show_consumption_patterns(self):
        st.subheader("Consumption Patterns Analysis")
        
        # Time period selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", self.data['timestamp'].min().date())
        with col2:
            end_date = st.date_input("End Date", self.data['timestamp'].max().date())
        
        # Filter data
        mask = (self.data['timestamp'].dt.date >= start_date) & (self.data['timestamp'].dt.date <= end_date)
        filtered_df = self.data.loc[mask]
        
        # Weekly pattern
        st.subheader("Weekly Consumption Pattern")
        weekly_pattern = filtered_df.groupby(filtered_df['timestamp'].dt.day_name())['consumption_kwh'].mean().reindex([
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ])
        
        fig = px.bar(x=weekly_pattern.index, y=weekly_pattern.values,
                    title="Average Consumption by Day of Week",
                    labels={'x': 'Day', 'y': 'Avg Consumption (kWh)'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Monthly trend
        st.subheader("Monthly Trend")
        monthly_trend = filtered_df.groupby(filtered_df['timestamp'].dt.to_period('M'))['consumption_kwh'].sum()
        
        fig = px.line(x=monthly_trend.index.astype(str), y=monthly_trend.values,
                     title="Monthly Consumption Trend",
                     labels={'x': 'Month', 'y': 'Total Consumption (kWh)'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap
        st.subheader("Consumption Heatmap")
        pivot_data = filtered_df.pivot_table(
            values='consumption_kwh',
            index=filtered_df['timestamp'].dt.hour,
            columns=filtered_df['timestamp'].dt.day_name(),
            aggfunc='mean'
        )
        
        fig = px.imshow(pivot_data, 
                       title="Hourly Consumption Heatmap by Day of Week",
                       labels={'x': 'Day of Week', 'y': 'Hour of Day', 'color': 'Avg Consumption (kWh)'})
        st.plotly_chart(fig, use_container_width=True)
    
    def show_cost_analysis(self):
        st.subheader("Cost Analysis")
        
        # Cost breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Cost", f"${self.data['cost'].sum():,.2f}")
            st.metric("Average Daily Cost", f"${self.data.groupby(self.data['timestamp'].dt.date)['cost'].sum().mean():.2f}")
        
        with col2:
            st.metric("Highest Daily Cost", f"${self.data.groupby(self.data['timestamp'].dt.date)['cost'].sum().max():.2f}")
            st.metric("Cost per kWh (Avg)", f"${self.data['rate_per_kwh'].mean():.4f}")
        
        # Cost trend
        daily_cost = self.data.groupby(self.data['timestamp'].dt.date)['cost'].sum().reset_index()
        daily_cost.columns = ['date', 'cost']
        
        fig = px.line(daily_cost, x='date', y='cost',
                     title="Daily Cost Trend",
                     labels={'cost': 'Cost ($)', 'date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Cost by category
        category_cost = self.data.groupby('category')['cost'].sum().reset_index()
        fig = px.pie(category_cost, values='cost', names='category',
                    title="Cost Distribution by Category")
        st.plotly_chart(fig, use_container_width=True)
    
    def show_efficiency_metrics(self):
        st.subheader("Efficiency Metrics")
        
        # Calculate efficiency metrics
        daily_stats = self.data.groupby(self.data['timestamp'].dt.date).agg({
            'consumption_kwh': ['sum', 'mean', 'std'],
            'cost': 'sum'
        }).round(2)
        
        daily_stats.columns = ['Total_Consumption', 'Avg_Consumption', 'Std_Consumption', 'Total_Cost']
        daily_stats['Efficiency_Score'] = (daily_stats['Avg_Consumption'] / daily_stats['Std_Consumption']).fillna(0)
        
        st.dataframe(daily_stats)
        
        # Efficiency trend
        fig = px.line(x=daily_stats.index, y=daily_stats['Efficiency_Score'],
                     title="Daily Efficiency Score Trend",
                     labels={'x': 'Date', 'y': 'Efficiency Score'})
        st.plotly_chart(fig, use_container_width=True)
    
    def show_peak_usage_analysis(self):
        st.subheader("Peak Usage Analysis")
        
        # Find peak hours
        hourly_avg = self.data.groupby(self.data['timestamp'].dt.hour)['consumption_kwh'].mean()
        peak_hour = hourly_avg.idxmax()
        peak_consumption = hourly_avg.max()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Peak Hour", f"{peak_hour}:00")
        with col2:
            st.metric("Peak Consumption", f"{peak_consumption:.2f} kWh")
        
        # Peak usage by day
        daily_peak = self.data.groupby(self.data['timestamp'].dt.date)['consumption_kwh'].max().reset_index()
        daily_peak.columns = ['date', 'peak_consumption']
        
        fig = px.bar(daily_peak, x='date', y='peak_consumption',
                    title="Daily Peak Consumption",
                    labels={'peak_consumption': 'Peak Consumption (kWh)', 'date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Peak usage by category
        category_peak = self.data.groupby('category')['consumption_kwh'].max().reset_index()
        fig = px.bar(category_peak, x='category', y='consumption_kwh',
                    title="Peak Consumption by Category",
                    labels={'consumption_kwh': 'Peak Consumption (kWh)'})
        st.plotly_chart(fig, use_container_width=True)