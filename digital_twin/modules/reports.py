import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import base64

class ReportGenerator:
    def __init__(self, data):
        self.data = data
    
    def show_reports_interface(self):
        st.subheader("Energy Reports Generator")
        
        tab1, tab2, tab3 = st.tabs(["Summary Report", "Detailed Analysis", "Custom Report"])
        
        with tab1:
            self.generate_summary_report()
        
        with tab2:
            self.generate_detailed_analysis()
        
        with tab3:
            self.generate_custom_report()
    
    def generate_summary_report(self):
        st.subheader("📊 Energy Consumption Summary Report")
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", self.data['timestamp'].min().date())
        with col2:
            end_date = st.date_input("End Date", self.data['timestamp'].max().date())
        
        # Filter data
        mask = (self.data['timestamp'].dt.date >= start_date) & (self.data['timestamp'].dt.date <= end_date)
        filtered_data = self.data.loc[mask]
        
        if filtered_data.empty:
            st.warning("No data available for the selected date range.")
            return
        
        # Generate report
        if st.button("Generate Summary Report"):
            self.create_summary_report(filtered_data, start_date, end_date)
    
    def create_summary_report(self, data, start_date, end_date):
        st.subheader(f"Summary Report: {start_date} to {end_date}")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_consumption = data['consumption_kwh'].sum()
            st.metric("Total Consumption", f"{total_consumption:,.2f} kWh")
        
        with col2:
            total_cost = data['cost'].sum()
            st.metric("Total Cost", f"${total_cost:,.2f}")
        
        with col3:
            avg_daily_consumption = data.groupby(data['timestamp'].dt.date)['consumption_kwh'].sum().mean()
            st.metric("Avg Daily Consumption", f"{avg_daily_consumption:.2f} kWh")
        
        with col4:
            avg_rate = data['rate_per_kwh'].mean()
            st.metric("Average Rate", f"${avg_rate:.4f}/kWh")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily consumption trend
            daily_consumption = data.groupby(data['timestamp'].dt.date)['consumption_kwh'].sum().reset_index()
            daily_consumption.columns = ['date', 'consumption']
            
            fig = px.line(daily_consumption, x='date', y='consumption',
                         title="Daily Consumption Trend")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Consumption by category
            category_consumption = data.groupby('category')['consumption_kwh'].sum().reset_index()
            
            fig = px.pie(category_consumption, values='consumption_kwh', names='category',
                        title="Consumption by Category")
            st.plotly_chart(fig, use_container_width=True)
        
        # Peak usage analysis
        st.subheader("Peak Usage Analysis")
        hourly_avg = data.groupby(data['timestamp'].dt.hour)['consumption_kwh'].mean()
        peak_hour = hourly_avg.idxmax()
        peak_consumption = hourly_avg.max()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Peak Hour", f"{peak_hour}:00")
        with col2:
            st.metric("Peak Consumption", f"{peak_consumption:.2f} kWh")
        with col3:
            lowest_hour = hourly_avg.idxmin()
            st.metric("Lowest Usage Hour", f"{lowest_hour}:00")
        
        # Recommendations
        self.generate_recommendations(data)
        
        # Export options
        self.show_export_options(data, "summary_report")
    
    def generate_detailed_analysis(self):
        st.subheader("📈 Detailed Energy Analysis")
        
        # Analysis options
        analysis_options = st.multiselect(
            "Select Analysis Components",
            ["Hourly Patterns", "Weekly Trends", "Monthly Comparison", "Device Analysis", "Location Analysis", "Cost Breakdown"],
            default=["Hourly Patterns", "Weekly Trends", "Cost Breakdown"]
        )
        
        if st.button("Generate Detailed Analysis"):
            for analysis in analysis_options:
                if analysis == "Hourly Patterns":
                    self.show_hourly_patterns()
                elif analysis == "Weekly Trends":
                    self.show_weekly_trends()
                elif analysis == "Monthly Comparison":
                    self.show_monthly_comparison()
                elif analysis == "Device Analysis":
                    self.show_device_analysis()
                elif analysis == "Location Analysis":
                    self.show_location_analysis()
                elif analysis == "Cost Breakdown":
                    self.show_cost_breakdown()
    
    def show_hourly_patterns(self):
        st.subheader("Hourly Consumption Patterns")
        
        hourly_data = self.data.groupby(self.data['timestamp'].dt.hour)['consumption_kwh'].agg(['mean', 'std']).reset_index()
        hourly_data.columns = ['hour', 'avg_consumption', 'std_consumption']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_data['hour'],
            y=hourly_data['avg_consumption'],
            mode='lines+markers',
            name='Average Consumption',
            error_y=dict(type='data', array=hourly_data['std_consumption'])
        ))
        
        fig.update_layout(
            title="Average Hourly Consumption with Standard Deviation",
            xaxis_title="Hour of Day",
            yaxis_title="Consumption (kWh)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def show_weekly_trends(self):
        st.subheader("Weekly Consumption Trends")
        
        weekly_data = self.data.groupby([
            self.data['timestamp'].dt.isocalendar().week,
            self.data['timestamp'].dt.day_name()
        ])['consumption_kwh'].sum().reset_index()
        
        weekly_data.columns = ['week', 'day', 'consumption']
        
        # Pivot for heatmap
        pivot_data = weekly_data.pivot(index='week', columns='day', values='consumption')
        
        fig = px.imshow(pivot_data, 
                       title="Weekly Consumption Heatmap",
                       labels={'x': 'Day of Week', 'y': 'Week Number', 'color': 'Consumption (kWh)'})
        st.plotly_chart(fig, use_container_width=True)
    
    def show_monthly_comparison(self):
        st.subheader("Monthly Consumption Comparison")
        
        monthly_data = self.data.groupby(self.data['timestamp'].dt.to_period('M')).agg({
            'consumption_kwh': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        monthly_data['month'] = monthly_data['timestamp'].astype(str)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly_data['month'],
            y=monthly_data['consumption_kwh'],
            name='Consumption (kWh)',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_data['month'],
            y=monthly_data['cost'],
            mode='lines+markers',
            name='Cost ($)',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Monthly Consumption and Cost Comparison",
            xaxis_title="Month",
            yaxis=dict(title="Consumption (kWh)", side="left"),
            yaxis2=dict(title="Cost ($)", side="right", overlaying="y")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def show_device_analysis(self):
        st.subheader("Device-wise Analysis")
        
        device_data = self.data.groupby('device').agg({
            'consumption_kwh': ['sum', 'mean', 'count'],
            'cost': 'sum'
        }).round(2)
        
        device_data.columns = ['Total Consumption', 'Avg Consumption', 'Usage Count', 'Total Cost']
        device_data = device_data.reset_index()
        
        st.dataframe(device_data)
        
        # Top consuming devices
        top_devices = device_data.nlargest(5, 'Total Consumption')
        
        fig = px.bar(top_devices, x='device', y='Total Consumption',
                    title="Top 5 Energy Consuming Devices")
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    def show_location_analysis(self):
        st.subheader("Location-wise Analysis")
        
        location_data = self.data.groupby('location').agg({
            'consumption_kwh': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(location_data, values='consumption_kwh', names='location',
                        title="Consumption by Location")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(location_data, values='cost', names='location',
                        title="Cost by Location")
            st.plotly_chart(fig, use_container_width=True)
    
    def show_cost_breakdown(self):
        st.subheader("Detailed Cost Breakdown")
        
        # Daily cost trend
        daily_cost = self.data.groupby(self.data['timestamp'].dt.date)['cost'].sum().reset_index()
        daily_cost.columns = ['date', 'cost']
        
        fig = px.line(daily_cost, x='date', y='cost',
                     title="Daily Cost Trend")
        st.plotly_chart(fig, use_container_width=True)
        
        # Cost statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Highest Daily Cost", f"${daily_cost['cost'].max():.2f}")
        with col2:
            st.metric("Lowest Daily Cost", f"${daily_cost['cost'].min():.2f}")
        with col3:
            st.metric("Average Daily Cost", f"${daily_cost['cost'].mean():.2f}")
        with col4:
            st.metric("Cost Std Deviation", f"${daily_cost['cost'].std():.2f}")
    
    def generate_custom_report(self):
        st.subheader("🎯 Custom Report Builder")
        
        # Custom report options
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Select Metrics**")
            metrics = st.multiselect(
                "Choose metrics to include",
                ["Total Consumption", "Total Cost", "Average Daily Consumption", 
                 "Peak Usage", "Efficiency Score", "Cost per kWh"],
                default=["Total Consumption", "Total Cost"]
            )
        
        with col2:
            st.write("**Select Visualizations**")
            charts = st.multiselect(
                "Choose charts to include",
                ["Daily Trend", "Category Breakdown", "Hourly Pattern", 
                 "Weekly Heatmap", "Device Analysis", "Location Analysis"],
                default=["Daily Trend", "Category Breakdown"]
            )
        
        # Filters
        st.write("**Filters**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_categories = st.multiselect(
                "Categories", 
                self.data['category'].unique(),
                default=self.data['category'].unique()
            )
        
        with col2:
            selected_locations = st.multiselect(
                "Locations",
                self.data['location'].unique(),
                default=self.data['location'].unique()
            )
        
        with col3:
            date_range = st.date_input(
                "Date Range",
                value=(self.data['timestamp'].min().date(), self.data['timestamp'].max().date()),
                min_value=self.data['timestamp'].min().date(),
                max_value=self.data['timestamp'].max().date()
            )
        
        if st.button("Generate Custom Report"):
            # Filter data based on selections
            filtered_data = self.data[
                (self.data['category'].isin(selected_categories)) &
                (self.data['location'].isin(selected_locations)) &
                (self.data['timestamp'].dt.date >= date_range[0]) &
                (self.data['timestamp'].dt.date <= date_range[1])
            ]
            
            self.create_custom_report(filtered_data, metrics, charts)
    
    def create_custom_report(self, data, metrics, charts):
        st.subheader("Custom Energy Report")
        
        # Display selected metrics
        if metrics:
            st.subheader("Key Metrics")
            cols = st.columns(len(metrics))
            
            for i, metric in enumerate(metrics):
                with cols[i]:
                    if metric == "Total Consumption":
                        value = data['consumption_kwh'].sum()
                        st.metric(metric, f"{value:,.2f} kWh")
                    elif metric == "Total Cost":
                        value = data['cost'].sum()
                        st.metric(metric, f"${value:,.2f}")
                    elif metric == "Average Daily Consumption":
                        value = data.groupby(data['timestamp'].dt.date)['consumption_kwh'].sum().mean()
                        st.metric(metric, f"{value:.2f} kWh")
                    elif metric == "Peak Usage":
                        value = data['consumption_kwh'].max()
                        st.metric(metric, f"{value:.2f} kWh")
                    elif metric == "Cost per kWh":
                        value = data['rate_per_kwh'].mean()
                        st.metric(metric, f"${value:.4f}")
        
        # Display selected charts
        if charts:
            for chart in charts:
                if chart == "Daily Trend":
                    daily_data = data.groupby(data['timestamp'].dt.date)['consumption_kwh'].sum().reset_index()
                    daily_data.columns = ['date', 'consumption']
                    fig = px.line