"""
LLM summarizer using Google Gemini for surf condition analysis.
"""

from google import genai
import os
from typing import Optional
from .prompt_templates import SURF_CONDITIONS_PROMPT, ONE_SENTENCE_SUMMARY_PROMPT


class SurfSummarizer:
    """Summarizer for surf conditions using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the summarizer with Gemini API key.
        
        Args:
            api_key: Google Gemini API key. If None, will try to get from environment.
        """
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = genai.Client(api_key=api_key)
    
    def get_surf_conditions(self, surf_beach: str, surf_data: dict = None, selected_date: str = None) -> str:
        """
        Get surf conditions summary for a specific beach using real surf data.
        
        Args:
            surf_beach: Name of the surf beach/break
            surf_data: Real surf data from Stormglass API (optional)
            selected_date: Selected date for analysis (optional)
            
        Returns:
            String containing surf conditions summary
        """
        try:
            if surf_data:
                # Format the surf data for the prompt
                formatted_data = self._format_surf_data(surf_data)
                prompt = SURF_CONDITIONS_PROMPT.format(
                    surf_beach=surf_beach, 
                    surf_data=formatted_data,
                    selected_date=selected_date or "today"
                )
            else:
                # Fallback to general knowledge if no data provided
                prompt = f"Provide general surf information about {surf_beach} surf break."
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error generating surf conditions: {str(e)}"
    
    def get_one_sentence_summary(self, beach_name: str, surf_data: dict, selected_date: str = None) -> str:
        """
        Get a one-sentence summary of surf conditions.
        
        Args:
            beach_name: Name of the surf beach/break
            surf_data: Real surf data from API
            selected_date: Selected date for analysis (optional)
            
        Returns:
            One-sentence summary of surf conditions
        """
        try:
            # Format the surf data for the prompt
            formatted_data = self._format_surf_data(surf_data)
            
            prompt = ONE_SENTENCE_SUMMARY_PROMPT.format(
                beach_name=beach_name,
                formatted_conditions=formatted_data,
                selected_date=selected_date or "today"
            )
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def _format_surf_data(self, surf_data: dict) -> str:
        """
        Format surf data into a readable string for the AI prompt.
        
        Args:
            surf_data: Dictionary containing surf data from Stormglass API
            
        Returns:
            Formatted string of surf data
        """
        try:
            if 'error' in surf_data:
                return f"Error retrieving surf data: {surf_data['error']}"
            
            # Handle Stormglass API data structure
            if 'data' in surf_data and 'hours' in surf_data['data']:
                # This is raw Stormglass data with nested structure
                hours_data = surf_data['data']['hours']
            elif 'hours' in surf_data:
                # This is Stormglass data with direct hours structure
                hours_data = surf_data['hours']
            else:
                # No hours data found
                return "No surf data available for this location and date."
            
            if not hours_data:
                return "No surf data available for this location and date."
            
            # Get current conditions (first hour)
            current_hour = hours_data[0]
            
            # Convert metric to imperial units
            wave_height_m = current_hour.get('waveHeight', {}).get('noaa', 0)
            wave_height_ft = round(float(wave_height_m) * 3.28084, 1) if wave_height_m != 'N/A' and wave_height_m != 0 else 'N/A'
            
            wind_speed_ms = current_hour.get('windSpeed', {}).get('noaa', 0)
            wind_speed_mph = round(float(wind_speed_ms) * 2.23694, 1) if wind_speed_ms != 'N/A' and wind_speed_ms != 0 else 'N/A'
            
            water_temp_c = current_hour.get('waterTemperature', {}).get('noaa', 0)
            water_temp_f = round((float(water_temp_c) * 9/5) + 32, 1) if water_temp_c != 'N/A' and water_temp_c != 0 else 'N/A'
            
            air_temp_c = current_hour.get('airTemperature', {}).get('noaa', 0)
            air_temp_f = round((float(air_temp_c) * 9/5) + 32, 1) if air_temp_c != 'N/A' and air_temp_c != 0 else 'N/A'
            
            visibility_km = current_hour.get('visibility', {}).get('noaa', 0)
            visibility_mi = round(float(visibility_km) * 0.621371, 1) if visibility_km != 'N/A' and visibility_km != 0 else 'N/A'
            
            formatted = f"""
CURRENT CONDITIONS (from Stormglass API):
- Wave Height: {wave_height_ft} ft
- Wave Period: {current_hour.get('wavePeriod', {}).get('noaa', 'N/A')} sec
- Wave Direction: {current_hour.get('waveDirection', {}).get('noaa', 'N/A')}°
- Wind Speed: {wind_speed_mph} mph
- Wind Direction: {current_hour.get('windDirection', {}).get('noaa', 'N/A')}°
- Water Temperature: {water_temp_f}°F
- Air Temperature: {air_temp_f}°F
- Pressure: {current_hour.get('pressure', {}).get('noaa', 'N/A')} mb
- Humidity: {current_hour.get('humidity', {}).get('noaa', 'N/A')}%
- Visibility: {visibility_mi} mi
- Cloud Cover: {current_hour.get('cloudCover', {}).get('noaa', 'N/A')}%

HOURLY FORECAST (Next 6 Hours):
"""
            
            # Add next 6 hours of data
            for i, hour in enumerate(hours_data[:6]):
                time_str = hour.get('time', 'N/A')[:16] if hour.get('time') else 'N/A'
                
                # Convert hourly data to imperial units
                hour_wave_height_m = hour.get('waveHeight', {}).get('noaa', 0)
                hour_wave_height_ft = round(float(hour_wave_height_m) * 3.28084, 1) if hour_wave_height_m != 'N/A' and hour_wave_height_m != 0 else 'N/A'
                
                hour_wind_speed_ms = hour.get('windSpeed', {}).get('noaa', 0)
                hour_wind_speed_mph = round(float(hour_wind_speed_ms) * 2.23694, 1) if hour_wind_speed_ms != 'N/A' and hour_wind_speed_ms != 0 else 'N/A'
                
                hour_water_temp_c = hour.get('waterTemperature', {}).get('noaa', 0)
                hour_water_temp_f = round((float(hour_water_temp_c) * 9/5) + 32, 1) if hour_water_temp_c != 'N/A' and hour_water_temp_c != 0 else 'N/A'
                
                hour_air_temp_c = hour.get('airTemperature', {}).get('noaa', 0)
                hour_air_temp_f = round((float(hour_air_temp_c) * 9/5) + 32, 1) if hour_air_temp_c != 'N/A' and hour_air_temp_c != 0 else 'N/A'
                
                formatted += f"""
Hour {i+1} ({time_str}):
- Waves: {hour_wave_height_ft}ft @ {hour.get('wavePeriod', {}).get('noaa', 'N/A')}s
- Wind: {hour_wind_speed_mph} mph @ {hour.get('windDirection', {}).get('noaa', 'N/A')}°
- Water Temp: {hour_water_temp_f}°F
- Air Temp: {hour_air_temp_f}°F
"""
            
            return formatted
            
        except Exception as e:
            return f"Error formatting surf data: {str(e)}"
