"""
LLM summarizer using Google Gemini for surf condition analysis.
"""

from google import genai
import os
from typing import Optional
from .prompt_templates import SURF_CONDITIONS_PROMPT


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
    
    def get_surf_conditions(self, surf_beach: str, surf_data: dict = None) -> str:
        """
        Get surf conditions summary for a specific beach using real surf data.
        
        Args:
            surf_beach: Name of the surf beach/break
            surf_data: Real surf data from Stormglass API (optional)
            
        Returns:
            String containing surf conditions summary
        """
        try:
            if surf_data:
                # Format the surf data for the prompt
                formatted_data = self._format_surf_data(surf_data)
                prompt = SURF_CONDITIONS_PROMPT.format(
                    surf_beach=surf_beach, 
                    surf_data=formatted_data
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
    
    def _format_surf_data(self, surf_data: dict) -> str:
        """
        Format surf data into a readable string for the AI prompt.
        
        Args:
            surf_data: Dictionary containing surf data
            
        Returns:
            Formatted string of surf data
        """
        try:
            if 'error' in surf_data:
                return f"Error retrieving surf data: {surf_data['error']}"
            
            # Get current conditions
            current_conditions = surf_data.get('current_conditions', {})
            
            # Get hourly data for today
            hourly_data = surf_data.get('hourly_conditions', [])
            
            formatted = f"""
CURRENT CONDITIONS:
- Wave Height: {current_conditions.get('wave_height', 'N/A')} ft
- Wave Period: {current_conditions.get('wave_period', 'N/A')} sec
- Wave Direction: {current_conditions.get('wave_direction', 'N/A')}°
- Wind Speed: {current_conditions.get('wind_speed', 'N/A')} mph
- Wind Direction: {current_conditions.get('wind_direction', 'N/A')}°
- Water Temperature: {current_conditions.get('water_temperature', 'N/A')}°F
- Air Temperature: {current_conditions.get('air_temperature', 'N/A')}°F
- Tide: {current_conditions.get('tide', 'N/A')} ft
- Pressure: {current_conditions.get('pressure', 'N/A')} mb
- Humidity: {current_conditions.get('humidity', 'N/A')}%
- Visibility: {current_conditions.get('visibility', 'N/A')} mi
- Cloud Cover: {current_conditions.get('cloud_cover', 'N/A')}%

HOURLY FORECAST (Next 6 Hours):
"""
            
            # Add next 6 hours of data
            for i, hour in enumerate(hourly_data[:6]):
                time_str = hour.get('time', 'N/A')[:16] if hour.get('time') else 'N/A'
                formatted += f"""
Hour {i+1} ({time_str}):
- Waves: {hour.get('wave_height', 'N/A')}ft @ {hour.get('wave_period', 'N/A')}s
- Wind: {hour.get('wind_speed', 'N/A')} mph @ {hour.get('wind_direction', 'N/A')}°
- Water Temp: {hour.get('water_temperature', 'N/A')}°F
- Tide: {hour.get('tide', 'N/A')} ft
"""
            
            return formatted
            
        except Exception as e:
            return f"Error formatting surf data: {str(e)}"
