import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

class EnergyCalculator:
    def __init__(self):
        self.appliances_db = {
            'LED Light Bulb (10W)': 0.01,
            'CFL Light Bulb (15W)': 0.015,
            'Incandescent Bulb (60W)': 0.06,
            'Desktop Computer': 0.3,
            'Laptop': 0.05,
            'Refrigerator': 0.15,
            'Air Conditioner (1 Ton)': 1.5,
            'Washing Machine': 0.5,
            'Microwave': 1.2,
            'Television (LED 32")': 0.08,
            'Water Heater': 3.0,
            'Dishwasher': 1.8,
            'Hair Dryer': 1.5,
            'Vacuum Cleaner': 1.4,
            'Electric Kettle': 2.0
        }
    
    def show_calculator_interface(self):
        st.subheader("Energy Cost Calculator")
        
        tab1, tab2, tab3 = st.tabs(["Single Appliance", "Multiple Appliances", "Bill Estimator"])
        
        with tab1:
            self.single_appliance_calculator()
        
        with tab2:
            self.multiple_appliances_calculator()
        
        with tab3:
            self.bill_estimator()
    
    def single_appliance_calculator(self):
        st.subheader("Single Appliance Calculator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            appliance = st.selectbox("Select Appliance", list(self.appliances_db.keys()))
            power_kw = st.number_input("Power (kW)", value=self.appliances_db[appliance], step=0.01)
            hours_per_day = st.number_input("Hours per day", min_value=0.0, max_value=24.0, value=8.0, step=0.5)
            days = st.number_input("Number of days", min_value=1, value=30)
        
        with col2:
            rate_per_kwh = st.number_input("Rate per kWh ($)", min_value=0.0, value=0.12, step=0.01)
            
            # Calculate consumption and cost
            daily_consumption = power_kw * hours_per_day
            total_consumption = daily_consumption * days
            daily_cost = daily_consumption * rate_per_kwh
            total_cost = total_consumption * rate_per_kwh
            
            # Display results
            st.metric("Daily Consumption", f"{daily_consumption:.2f} kWh")
            st.metric("Total Consumption", f"{total_consumption:.2f} kWh")
            st.metric("Daily Cost", f"${daily_cost:.2f}")
            st.metric("Total Cost", f"${total_cost:.2f}")
        
        # Cost breakdown chart
        if st.button("Show Cost Breakdown"):
            self.show_cost_breakdown(appliance, daily_cost, days)
    
    def multiple_appliances_calculator(self):
        st.subheader("Multiple Appliances Calculator")
        
        # Initialize session state for appliances list
        if 'appliances_list' not in st.session_state:
            st.session_state.appliances_list = []
        
        # Add appliance form
        with st.form("add_appliance"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                appliance = st.selectbox("Appliance", list(self.appliances_db.keys()))
            with col2:
                power = st.number_input("Power (kW)", value=self.appliances_db[appliance], step=0.01)
            with col3:
                hours = st.number_input("Hours/day", min_value=0.0, max_value=24.0, value=8.0, step=0.5)
            with col4:
                quantity = st.number_input("Quantity", min_value=1, value=1)
            
            submitted = st.form_submit_button("Add Appliance")
            
            if submitted:
                appliance_data = {
                    'appliance': appliance,
                    'power_kw': power,
                    'hours_per_day': hours,
                    'quantity': quantity,
                    'daily_consumption': power * hours * quantity,
                    'daily_cost': power * hours * quantity * 0.12  # Default rate
                }
                st.session_state.appliances_list.append(appliance_data)
                st.success(f"Added {appliance}")
        
        # Display appliances list
        if st.session_state.appliances_list:
            df = pd.DataFrame(st.session_state.appliances_list)
            
            # Rate input
            rate = st.number_input("Rate per kWh ($)", min_value=0.0, value=0.12, step=0.01, key="multi_rate")
            days = st.number_input("Number of days", min_value=1, value=30, key="multi_days")
            
            # Recalculate costs with current rate
            df['daily_cost'] = df['daily_consumption'] * rate
            df['total_consumption'] = df['daily_consumption'] * days
            df['total_cost'] = df['daily_cost'] * days
            
            # Display results
            st.subheader("Appliances Summary")
            st.dataframe(df)
            
            # Total calculations
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Daily Consumption", f"{df['daily_consumption'].sum():.2f} kWh")
            with col2:
                st.metric("Total Daily Cost", f"${df['daily_cost'].sum():.2f}")
            with col3:
                st.metric(f"Total Cost ({days} days)", f"${df['total_cost'].sum():.2f}")
            
            # Consumption breakdown chart
            fig = px.pie(df, values='daily_consumption', names='appliance',
                        title="Daily Consumption Breakdown")
            st.plotly_chart(fig, use_container_width=True)
            
            # Cost breakdown chart
            fig = px.bar(df, x='appliance', y='daily_cost',
                        title="Daily Cost by Appliance")
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Clear list button
            if st.button("Clear All Appliances"):
                st.session_state.appliances_list = []
                st.experimental_rerun()
    
    def bill_estimator(self):
        st.subheader("Monthly Bill Estimator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Household Information**")
            household_size = st.selectbox("Household Size", [1, 2, 3, 4, 5, "6+"])
            home_type = st.selectbox("Home Type", ["Apartment", "House", "Condo"])
            climate_zone = st.selectbox("Climate Zone", ["Hot", "Moderate", "Cold"])
            
        with col2:
            st.write("**Usage Patterns**")
            ac_usage = st.slider("AC Usage (hours/day)", 0, 24, 8)
            heating_usage = st.slider("Heating Usage (hours/day)", 0, 24, 6)
            lighting_hours = st.slider("Lighting Usage (hours/day)", 0, 24, 6)
        
        # Estimate consumption based on inputs
        base_consumption = self.estimate_base_consumption(household_size, home_type)
        climate_adjustment = self.get_climate_adjustment(climate_zone)
        
        # Calculate estimated consumption
        estimated_daily = base_consumption * climate_adjustment
        estimated_monthly = estimated_daily * 30
        
        # Rate structure
        st.subheader("Rate Structure")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            base_rate = st.number_input("Base Rate ($/kWh)", value=0.12, step=0.01)
        with col2:
            peak_rate = st.number_input("Peak Rate ($/kWh)", value=0.18, step=0.01)
        with col3:
            off_peak_rate = st.number_input("Off-Peak Rate ($/kWh)", value=0.08, step=0.01)
        
        # Calculate estimated bill
        peak_hours_consumption = estimated_monthly * 0.3  # 30% during peak hours
        off_peak_consumption = estimated_monthly * 0.2    # 20% during off-peak
        base_consumption_calc = estimated_monthly * 0.5   # 50% during base hours
        
        estimated_bill = (peak_hours_consumption * peak_rate + 
                         off_peak_consumption * off_peak_rate + 
                         base_consumption_calc * base_rate)
        
        # Display results
        st.subheader("Estimated Monthly Bill")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Estimated Consumption", f"{estimated_monthly:.0f} kWh")
        with col2:
            st.metric("Estimated Bill", f"${estimated_bill:.2f}")
        with col3:
            st.metric("Average Rate", f"${estimated_bill/estimated_monthly:.4f}/kWh")
        
        # Bill breakdown
        st.subheader("Bill Breakdown")
        breakdown_data = {
            'Rate Type': ['Peak Hours', 'Off-Peak Hours', 'Base Hours'],
            'Consumption (kWh)': [peak_hours_consumption, off_peak_consumption, base_consumption_calc],
            'Rate ($/kWh)': [peak_rate, off_peak_rate, base_rate],
            'Cost ($)': [peak_hours_consumption * peak_rate, 
                        off_peak_consumption * off_peak_rate, 
                        base_consumption_calc * base_rate]
        }
        
        breakdown_df = pd.DataFrame(breakdown_data)
        st.dataframe(breakdown_df)
        
        # Visualization
        fig = px.bar(breakdown_df, x='Rate Type', y='Cost ($)',
                    title="Cost Breakdown by Rate Type")
        st.plotly_chart(fig, use_container_width=True)
        
        # Savings recommendations
        self.show_savings_recommendations(estimated_monthly, estimated_bill)
    
    def estimate_base_consumption(self, household_size, home_type):
        """Estimate base daily consumption based on household characteristics"""
        base_consumption = {
            1: 15,
            2: 25,
            3: 35,
            4: 45,
            5: 55,
            "6+": 65
        }
        
        home_multiplier = {
            "Apartment": 0.8,
            "Condo": 0.9,
            "House": 1.2
        }
        
        return base_consumption[household_size] * home_multiplier[home_type]
    
    def get_climate_adjustment(self, climate_zone):
        """Get climate adjustment factor"""
        adjustments = {
            "Hot": 1.3,
            "Moderate": 1.0,
            "Cold": 1.2
        }
        return adjustments[climate_zone]
    
    def show_cost_breakdown(self, appliance, daily_cost, days):
        """Show cost breakdown visualization"""
        # Create daily cost projection
        dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
        costs = [daily_cost] * days
        cumulative_costs = np.cumsum(costs)
        
        df = pd.DataFrame({
            'Date': dates,
            'Daily Cost': costs,
            'Cumulative Cost': cumulative_costs
        })
        
        # Create subplot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Daily Cost'],
            mode='lines',
            name='Daily Cost',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Cumulative Cost'],
            mode='lines',
            name='Cumulative Cost',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title=f"Cost Projection for {appliance}",
            xaxis_title="Date",
            yaxis=dict(title="Daily Cost ($)", side="left"),
            yaxis2=dict(title="Cumulative Cost ($)", side="right", overlaying="y"),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def show_savings_recommendations(self, monthly_consumption, monthly_bill):
        """Show energy savings recommendations"""
        st.subheader("💡 Energy Savings Recommendations")
        
        recommendations = [
            {
                "tip": "Switch to LED bulbs",
                "savings": "Up to 75% lighting cost reduction",
                "potential_monthly_savings": monthly_bill * 0.15
            },
            {
                "tip": "Use programmable thermostat",
                "savings": "10-15% heating/cooling cost reduction",
                "potential_monthly_savings": monthly_bill * 0.12
            },
            {
                "tip": "Unplug devices when not in use",
                "savings": "5-10% total bill reduction",
                "potential_monthly_savings": monthly_bill * 0.075
            },
            {
                "tip": "Use energy-efficient appliances",
                "savings": "20-30% appliance cost reduction",
                "potential_monthly_savings": monthly_bill * 0.25
            },
            {
                "tip": "Optimize peak hour usage",
                "savings": "15-20% bill reduction",
                "potential_monthly_savings": monthly_bill * 0.175
            }
        ]
        
        for i, rec in enumerate(recommendations, 1):
            with st.expander(f"Tip {i}: {rec['tip']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Potential Savings:** {rec['savings']}")
                with col2:
                    st.write(f"**Monthly Savings:** ${rec['potential_monthly_savings']:.2f}")
        
        # Total potential savings
        total_potential_savings = sum(rec['potential_monthly_savings'] for rec in recommendations)
        st.success(f"**Total Potential Monthly Savings: ${total_potential_savings:.2f}**")
        st.info(f"**Potential Annual Savings: ${total_potential_savings * 12:.2f}**")