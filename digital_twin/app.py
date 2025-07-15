import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
from streamlit_option_menu import option_menu
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

# Configure page
st.set_page_config(
    page_title="Energy Consumption Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modules
from modules.data_generator import generate_sample_data
from modules.analytics import EnergyAnalytics
from modules.forecasting import EnergyForecasting
from modules.calculator import EnergyCalculator
from modules.reports import ReportGenerator

def main():
    st.title("⚡ Energy Consumption Analytics Dashboard")
    
    # Initialize session state
    if 'energy_data' not in st.session_state:
        st.session_state.energy_data = generate_sample_data()
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Data Input", "Analytics", "Forecasting", "Calculator", "Reports"],
        icons=["speedometer2", "upload", "graph-up", "crystal-ball", "calculator", "file-earmark-text"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )
    
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Data Input":
        show_data_input()
    elif selected == "Analytics":
        show_analytics()
    elif selected == "Forecasting":
        show_forecasting()
    elif selected == "Calculator":
        show_calculator()
    elif selected == "Reports":
        show_reports()

def show_dashboard():
    st.header("📊 Energy Consumption Dashboard")
    
    df = st.session_state.energy_data
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_consumption = df['consumption_kwh'].sum()
        st.metric("Total Consumption", f"{total_consumption:,.2f} kWh")
    
    with col2:
        avg_daily = df.groupby(df['timestamp'].dt.date)['consumption_kwh'].sum().mean()
        st.metric("Avg Daily Consumption", f"{avg_daily:.2f} kWh")
    
    with col3:
        total_cost = df['cost'].sum()
        st.metric("Total Cost", f"${total_cost:,.2f}")
    
    with col4:
        avg_rate = df['rate_per_kwh'].mean()
        st.metric("Avg Rate", f"${avg_rate:.4f}/kWh")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Daily Consumption Trend")
        daily_consumption = df.groupby(df['timestamp'].dt.date)['consumption_kwh'].sum().reset_index()
        daily_consumption.columns = ['date', 'consumption']
        
        fig = px.line(daily_consumption, x='date', y='consumption',
                     title="Daily Energy Consumption",
                     labels={'consumption': 'Consumption (kWh)', 'date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Consumption by Category")
        category_consumption = df.groupby('category')['consumption_kwh'].sum().reset_index()
        
        fig = px.pie(category_consumption, values='consumption_kwh', names='category',
                    title="Energy Consumption by Category")
        st.plotly_chart(fig, use_container_width=True)
    
    # Hourly pattern
    st.subheader("Hourly Consumption Pattern")
    hourly_pattern = df.groupby(df['timestamp'].dt.hour)['consumption_kwh'].mean().reset_index()
    hourly_pattern.columns = ['hour', 'avg_consumption']
    
    fig = px.bar(hourly_pattern, x='hour', y='avg_consumption',
                title="Average Hourly Consumption Pattern",
                labels={'avg_consumption': 'Avg Consumption (kWh)', 'hour': 'Hour of Day'})
    st.plotly_chart(fig, use_container_width=True)

def show_data_input():
    st.header("📤 Data Input & Management")
    
    tab1, tab2, tab3 = st.tabs(["Upload Data", "Manual Entry", "Database Connection"])
    
    with tab1:
        st.subheader("Upload Energy Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV file", 
            type=['csv', 'xlsx'],
            help="Upload your energy consumption data"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success("File uploaded successfully!")
                st.dataframe(df.head())
                
                # Data validation and processing
                if st.button("Process Data"):
                    if 'timestamp' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                    st.session_state.energy_data = df
                    st.success("Data processed and saved!")
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    with tab2:
        st.subheader("Manual Data Entry")
        
        with st.form("manual_entry"):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date", datetime.now().date())
                time = st.time_input("Time", datetime.now().time())
                consumption = st.number_input("Consumption (kWh)", min_value=0.0, step=0.1)
                rate = st.number_input("Rate per kWh ($)", min_value=0.0, step=0.001, value=0.12)
            
            with col2:
                category = st.selectbox("Category", 
                    ["Lighting", "HVAC", "Equipment", "Other"])
                device = st.text_input("Device/Equipment")
                location = st.text_input("Location")
                notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("Add Entry")
            
            if submitted:
                new_entry = {
                    'timestamp': datetime.combine(date, time),
                    'consumption_kwh': consumption,
                    'rate_per_kwh': rate,
                    'cost': consumption * rate,
                    'category': category,
                    'device': device,
                    'location': location,
                    'notes': notes
                }
                
                if 'energy_data' not in st.session_state:
                    st.session_state.energy_data = pd.DataFrame([new_entry])
                else:
                    st.session_state.energy_data = pd.concat([
                        st.session_state.energy_data, 
                        pd.DataFrame([new_entry])
                    ], ignore_index=True)
                
                st.success("Entry added successfully!")
    
    with tab3:
        st.subheader("Database Connection")
        st.info("Database connection features can be implemented here")

def show_analytics():
    st.header("📈 Energy Analytics")
    
    if 'energy_data' not in st.session_state:
        st.warning("Please upload or enter energy data first.")
        return
    
    df = st.session_state.energy_data
    analytics = EnergyAnalytics(df)
    
    # Analytics options
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Consumption Patterns", "Cost Analysis", "Efficiency Metrics", "Peak Usage Analysis"]
    )
    
    if analysis_type == "Consumption Patterns":
        analytics.show_consumption_patterns()
    elif analysis_type == "Cost Analysis":
        analytics.show_cost_analysis()
    elif analysis_type == "Efficiency Metrics":
        analytics.show_efficiency_metrics()
    elif analysis_type == "Peak Usage Analysis":
        analytics.show_peak_usage_analysis()

def show_forecasting():
    st.header("🔮 Energy Consumption Forecasting")
    
    if 'energy_data' not in st.session_state:
        st.warning("Please upload or enter energy data first.")
        return
    
    df = st.session_state.energy_data
    forecasting = EnergyForecasting(df)
    forecasting.show_forecasting_interface()

def show_calculator():
    st.header("🧮 Energy Cost Calculator")
    
    calculator = EnergyCalculator()
    calculator.show_calculator_interface()

def show_reports():
    st.header("📄 Energy Reports")
    
    if 'energy_data' not in st.session_state:
        st.warning("Please upload or enter energy data first.")
        return
    
    df = st.session_state.energy_data
    report_generator = ReportGenerator(df)
    report_generator.show_reports_interface()

if __name__ == "__main__":
    main()
