"""
WaveWatch - Surf Conditions App
A simple Streamlit app to get surf conditions for any beach.
"""

import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv
from src.wavewatch.llm.summarizer import SurfSummarizer
from src.wavewatch.api.data_fetcher import StormglassDataFetcher

# Load environment variables from .env file
load_dotenv()

def create_surf_charts(hourly_data):
    """Create line charts for surf conditions throughout the day."""
    if 'error' in hourly_data or not hourly_data.get('hourly_conditions'):
        return None
    
    try:
        # Convert hourly data to DataFrame
        hours = hourly_data['hourly_conditions']
        df_data = []
        
        # Get current date to filter out next day's data
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        for hour in hours:
            hour_time = hour.get('time', '')
            # Only include data from current day
            if hour_time.startswith(current_date):
                df_data.append({
                    'time': hour_time,
                    'wave_height': float(hour.get('wave_height', 0)) if hour.get('wave_height') != 'N/A' else 0,
                    'wave_period': float(hour.get('wave_period', 0)) if hour.get('wave_period') != 'N/A' else 0,
                    'wind_speed': float(hour.get('wind_speed', 0)) if hour.get('wind_speed') != 'N/A' else 0,
                    'tide': float(hour.get('tide', 0)) if hour.get('tide') != 'N/A' else 0,
                    'air_temperature': float(hour.get('air_temperature', 0)) if hour.get('air_temperature') != 'N/A' else 0,
                    'humidity': float(hour.get('humidity', 0)) if hour.get('humidity') != 'N/A' else 0,
                    'water_temperature': float(hour.get('water_temperature', 0)) if hour.get('water_temperature') != 'N/A' else 0
                })
        
        df = pd.DataFrame(df_data)
        
        # Parse time for better x-axis
        df['time_parsed'] = pd.to_datetime(df['time']).dt.strftime('%H:%M')
        
        # Create charts
        charts = {}
        
        # Wave Height Chart
        fig_wave = px.line(df, x='time_parsed', y='wave_height', 
                          title='🌊 Wave Height Throughout the Day',
                          labels={'wave_height': 'Wave Height (ft)', 'time_parsed': 'Time'})
        fig_wave.update_layout(height=300, showlegend=False)
        charts['wave_height'] = fig_wave
        
        # Wave Period Chart
        fig_period = px.line(df, x='time_parsed', y='wave_period',
                            title='⏱️ Wave Period Throughout the Day',
                            labels={'wave_period': 'Wave Period (sec)', 'time_parsed': 'Time'})
        fig_period.update_layout(height=300, showlegend=False)
        charts['wave_period'] = fig_period
        
        # Wind Speed Chart
        fig_wind = px.line(df, x='time_parsed', y='wind_speed',
                          title='💨 Wind Speed Throughout the Day',
                          labels={'wind_speed': 'Wind Speed (mph)', 'time_parsed': 'Time'})
        fig_wind.update_layout(height=300, showlegend=False)
        charts['wind_speed'] = fig_wind
        
        # Tide Chart
        fig_tide = px.line(df, x='time_parsed', y='tide',
                          title='🌊 Tide Throughout the Day',
                          labels={'tide': 'Tide (ft)', 'time_parsed': 'Time'})
        fig_tide.update_layout(height=300, showlegend=False)
        charts['tide'] = fig_tide
        
        # Air Temperature Chart
        fig_air_temp = px.line(df, x='time_parsed', y='air_temperature',
                              title='🌡️ Air Temperature Throughout the Day',
                              labels={'air_temperature': 'Air Temperature (°F)', 'time_parsed': 'Time'})
        fig_air_temp.update_layout(height=300, showlegend=False)
        charts['air_temperature'] = fig_air_temp
        
        # Humidity Chart
        fig_humidity = px.line(df, x='time_parsed', y='humidity',
                              title='💧 Humidity Throughout the Day',
                              labels={'humidity': 'Humidity (%)', 'time_parsed': 'Time'})
        fig_humidity.update_layout(height=300, showlegend=False)
        charts['humidity'] = fig_humidity
        
        # Water Temperature Chart
        fig_water_temp = px.line(df, x='time_parsed', y='water_temperature',
                                title='🏊 Water Temperature Throughout the Day',
                                labels={'water_temperature': 'Water Temperature (°F)', 'time_parsed': 'Time'})
        fig_water_temp.update_layout(height=300, showlegend=False)
        charts['water_temperature'] = fig_water_temp
        
        return charts
        
    except Exception as e:
        st.error(f"Error creating charts: {str(e)}")
        return None

# Configure page
st.set_page_config(
    page_title="WaveWatch",
    page_icon="🏄‍♂️",
    layout="wide"
)

def main():
    """Main Streamlit app function."""
    
    # Get API keys from environment
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    stormglass_api_key = os.getenv('STORMGLASS_API_KEY')
    
    if not gemini_api_key:
        st.error("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        st.stop()
    
    if not stormglass_api_key:
        st.error("STORMGLASS_API_KEY not found in environment variables. Please check your .env file.")
        st.stop()
    
    # Header
    st.title("🏄‍♂️ WaveWatch")
    st.subheader("Get surf conditions for any beach")
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Beach Input")
        surf_beach = st.text_input(
            "Enter surf beach name:",
            placeholder="e.g., Pleasure Point, Malibu, Pipeline, Scripps",
            help="Enter the name of the surf break you want to check"
        )
        
        # Data source selection
        st.subheader("Data Sources")
        show_real_data = st.checkbox("Show Real Surf Data", value=True, help="Display actual surf conditions from Stormglass API")
        show_ai_analysis = st.checkbox("Show AI Analysis", value=True, help="Display AI-generated surf analysis")
        
        if st.button("Get Surf Conditions", type="primary"):
            if not surf_beach:
                st.error("Please enter a beach name.")
            else:
                with st.spinner("Fetching surf conditions..."):
                    try:
                        # Initialize data fetcher and summarizer
                        data_fetcher = StormglassDataFetcher(api_key=stormglass_api_key)
                        summarizer = SurfSummarizer(api_key=gemini_api_key)
                        
                        # Store in session state for display
                        st.session_state.beach = surf_beach
                        st.session_state.show_real_data = show_real_data
                        st.session_state.show_ai_analysis = show_ai_analysis
                        
                        # Get real surf data
                        if show_real_data:
                            st.session_state.real_data = data_fetcher.get_current_conditions(surf_beach)
                            st.session_state.hourly_data = data_fetcher.get_hourly_conditions(surf_beach)
                            st.session_state.best_times = data_fetcher.get_best_surf_times(surf_beach)
                        
                        # Get AI analysis with real surf data
                        if show_ai_analysis:
                            # Combine current and hourly data for AI analysis
                            combined_data = {
                                'current_conditions': st.session_state.real_data.get('current_conditions', {}),
                                'hourly_conditions': st.session_state.hourly_data.get('hourly_conditions', [])
                            }
                            st.session_state.ai_analysis = summarizer.get_surf_conditions(surf_beach, combined_data)
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with col2:
        st.header("Surf Conditions")
        
        if hasattr(st.session_state, 'beach') and st.session_state.beach:
            st.subheader(f"Conditions for {st.session_state.beach}")
            
            # Display real surf data
            if st.session_state.show_real_data and hasattr(st.session_state, 'real_data'):
                if 'error' in st.session_state.real_data:
                    st.error(f"Real data error: {st.session_state.real_data['error']}")
                else:
                    st.markdown("### 🌊 Real Surf Data")
                    real_data = st.session_state.real_data['current_conditions']
                    
                    # Create columns for data display
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("Wave Height", f"{real_data['wave_height']} ft")
                        st.metric("Wave Period", f"{real_data['wave_period']} sec")
                        st.metric("Wind Speed", f"{real_data['wind_speed']} mph")
                    
                    with col_b:
                        st.metric("Water Temp", f"{real_data['water_temperature']}°F")
                        st.metric("Air Temp", f"{real_data['air_temperature']}°F")
                        st.metric("Tide", f"{real_data['tide']} ft")
                    
                    with col_c:
                        st.metric("Pressure", f"{real_data['pressure']} mb")
                        st.metric("Humidity", f"{real_data['humidity']}%")
                        st.metric("Visibility", f"{real_data['visibility']} mi")
                    
                    # Show cache status
                    if st.session_state.real_data.get('cached', False):
                        st.success("✅ Data from cache (no API call made)")
                    else:
                        st.info("🔄 Fresh data from API")
            
            # Display hourly data
            if st.session_state.show_real_data and hasattr(st.session_state, 'hourly_data'):
                if 'error' not in st.session_state.hourly_data:
                    st.markdown("### 📅 Hourly Forecast")
                    
                    # Show next 6 hours
                    hourly_data = st.session_state.hourly_data['hourly_conditions'][:6]
                    
                    for hour in hourly_data:
                        with st.expander(f"🕐 {hour['time'][:16]} - {hour['wave_height']}ft waves"):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.write(f"**Waves:** {hour['wave_height']}ft @ {hour['wave_period']}s")
                                st.write(f"**Wind:** {hour['wind_speed']} mph @ {hour['wind_direction']}°")
                            with col_b:
                                st.write(f"**Water:** {hour['water_temperature']}°F")
                                st.write(f"**Tide:** {hour['tide']} ft")
            
            # Display best surf times
            if st.session_state.show_real_data and hasattr(st.session_state, 'best_times'):
                if 'error' not in st.session_state.best_times:
                    st.markdown("### 🏆 Best Surf Times Today")
                    best_times = st.session_state.best_times['best_times'][:3]
                    
                    for i, time_slot in enumerate(best_times, 1):
                        st.write(f"**{i}.** {time_slot['time'][:16]} - {time_slot['wave_height']}ft waves, {time_slot['wind_speed']} mph wind (Score: {time_slot['score']:.1f})")
            
            # Display surf condition charts
            if st.session_state.show_real_data and hasattr(st.session_state, 'hourly_data'):
                if 'error' not in st.session_state.hourly_data:
                    st.markdown("### 📊 Surf Conditions Throughout the Day")
                    
                    # Create charts
                    charts = create_surf_charts(st.session_state.hourly_data)
                    
                    if charts:
                        # Display charts in a grid
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.plotly_chart(charts['wave_height'], use_container_width=True)
                            st.plotly_chart(charts['wave_period'], use_container_width=True)
                            st.plotly_chart(charts['wind_speed'], use_container_width=True)
                            st.plotly_chart(charts['tide'], use_container_width=True)
                        
                        with col2:
                            st.plotly_chart(charts['air_temperature'], use_container_width=True)
                            st.plotly_chart(charts['humidity'], use_container_width=True)
                            st.plotly_chart(charts['water_temperature'], use_container_width=True)
            
            # Display AI analysis
            if st.session_state.show_ai_analysis and hasattr(st.session_state, 'ai_analysis'):
                st.markdown("### 🤖 AI Surf Analysis")
                st.markdown("---")
                st.markdown(st.session_state.ai_analysis)
                
                # Add a download button for the AI analysis
                st.download_button(
                    label="Download AI Analysis",
                    data=st.session_state.ai_analysis,
                    file_name=f"{st.session_state.beach.replace(' ', '_')}_ai_analysis.txt",
                    mime="text/plain"
                )
        else:
            st.info("Enter a beach name and click 'Get Surf Conditions' to see the analysis.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**WaveWatch** - Powered by Google Gemini AI & Stormglass API | "
        "Get API keys: [Google AI Studio](https://makersuite.google.com/app/apikey) | [Stormglass](https://stormglass.io)"
    )

if __name__ == "__main__":
    main()
