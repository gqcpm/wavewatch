"""
WaveWatch - Surf Conditions App
A simple Streamlit app to get surf conditions for any beach.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from src.wavewatch.llm.summarizer import SurfSummarizer
from src.wavewatch.api.data_fetcher import StormglassDataFetcher

# Load environment variables from .env file
load_dotenv()

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
