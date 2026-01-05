"""
LLM summarizer using Google Gemini for surf condition analysis.
"""

from google import genai
import os
import re
from typing import Optional, List, Dict
from .prompt_templates import (
    CONDITIONS_COMPARISON_PROMPT,
    ONE_SENTENCE_SUMMARY_PROMPT,
    IDEAL_CONDITIONS_EXTRACTION_PROMPT,
)

# Import RAG components (with fallback if not available)
try:
    from ..rag.knowledge_base import beach_has_knowledge_base
    from ..rag.retriever import RAGRetriever
    RAG_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    RAG_AVAILABLE = False
    beach_has_knowledge_base = None
    RAGRetriever = None


class SurfSummarizer:
    """Summarizer for surf conditions using Google Gemini."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the summarizer with Gemini API key.

        Args:
            api_key: Google Gemini API key. If None, will try to get from environment.
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter."
            )

        self.client = genai.Client(api_key=api_key)

    def _generate_ideal_conditions(self, beach_name: str) -> str:
        """
        Generate ideal conditions for a specific break.
        Uses RAG if knowledge base exists, otherwise falls back to LLM general knowledge.

        Args:
            beach_name: Name of the beach/break

        Returns:
            Ideal conditions as formatted string
        """
        # Check if RAG is available and knowledge base exists
        use_rag = False
        rag_context = ""
        
        if RAG_AVAILABLE and beach_has_knowledge_base(beach_name):
            try:
                print(f"📚 Using RAG knowledge base for {beach_name}")
                # Initialize retriever without auto-initializing index (in case it doesn't exist)
                retriever = RAGRetriever(initialize_index=False)
                
                # Try to initialize index, but don't fail if it doesn't exist
                try:
                    retriever.vector_store.initialize_index()
                    index_available = True
                except Exception as idx_error:
                    print(f"⚠️ Pinecone index not available, falling back to LLM: {idx_error}")
                    index_available = False
                
                if index_available:
                    # Retrieve relevant context about ideal conditions
                    query = f"ideal conditions for {beach_name} surf break"
                    results = retriever.retrieve(
                        query=query,
                        beach_name=beach_name,
                        top_k=5,
                    )
                    
                    if results:
                        rag_context = retriever.format_context(results, max_length=1500)
                        use_rag = True
                        print(f"✅ Retrieved {len(results)} relevant chunks from knowledge base")
                    else:
                        print(f"⚠️ No results found in knowledge base, falling back to LLM")
            except Exception as e:
                print(f"⚠️ Error using RAG, falling back to LLM: {e}")
        else:
            if not RAG_AVAILABLE:
                print(f"📝 RAG not available, using LLM general knowledge for {beach_name}")
            else:
                print(f"📝 No knowledge base found for {beach_name}, using LLM general knowledge")
        
        # Build prompt with or without RAG context
        try:
            if use_rag and rag_context:
                # RAG-enhanced prompt
                search_results = f"""The following information was retrieved from the knowledge base about {beach_name}:

{rag_context}

Use this retrieved knowledge as the primary source for ideal conditions. If the retrieved information doesn't cover all aspects, supplement with your general knowledge about similar breaks and surf forecasting principles."""
            else:
                # Original LLM-only prompt
                search_results = "Use your general knowledge about this surf break. If you don't have specific knowledge about this exact break, use your understanding of similar breaks and general surf forecasting principles."
            
            prompt = IDEAL_CONDITIONS_EXTRACTION_PROMPT.format(
                beach_name=beach_name, 
                search_results=search_results
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite", contents=prompt
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                return f"⚠️ Gemini API rate limit exceeded while generating ideal conditions. \
                No ideal conditions information available. Using general surf forecasting principles. (Error: {error_msg})"
            print(f"Error generating ideal conditions: {error_msg}")
            return "Error generating ideal conditions. Using general surf forecasting principles."

    def get_surf_conditions(
        self,
        surf_beach: str,
        surf_data: dict = None,
        selected_date: str = None,
        use_break_specific: bool = True,
    ) -> tuple:
        """
        Get surf conditions summary for a specific beach using real surf data.

        Args:
            surf_beach: Name of the surf beach/break
            surf_data: Real surf data from Stormglass API (optional)
            selected_date: Selected date for analysis (optional)

        Returns:
            Tuple of (surf conditions summary, ideal_conditions)
        """
        try:
            if surf_data:
                # Step 1: Get ideal conditions (if enabled)
                ideal_conditions = "No ideal conditions information available. Using general surf forecasting principles."

                if use_break_specific:
                    print(
                        f"📝 Generating ideal conditions for {surf_beach} using LLM knowledge..."
                    )
                    ideal_conditions = self._generate_ideal_conditions(surf_beach)
                    print("✅ Ideal conditions generated")
                else:
                    ideal_conditions = "No ideal conditions information available. Using general surf forecasting principles."

                # Format the surf data for the prompt
                formatted_data = self._format_surf_data(surf_data)

                # Step 2: Generate final forecast by comparing current conditions to ideal conditions
                prompt = CONDITIONS_COMPARISON_PROMPT.format(
                    surf_beach=surf_beach,
                    ideal_conditions=ideal_conditions,
                    surf_data=formatted_data,
                    selected_date=selected_date or "today",
                )
            else:
                # Fallback to general knowledge if no data provided
                prompt = (
                    f"Provide general surf information about {surf_beach} surf break."
                )
                ideal_conditions = ""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite", contents=prompt
            )
            return response.text, ideal_conditions if 'ideal_conditions' in locals() else ""
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print("⚠️ Gemini API rate limit exceeded. Check your quota at https://console.cloud.google.com/apis/dashboard")
                return (
                    f"⚠️ API rate limit exceeded. Please check your Google Cloud Console for quota usage. \
                    If you haven't used this API recently, your key may be compromised - consider rotating it. (Error: {error_msg})",
                    ideal_conditions if 'ideal_conditions' in locals() else ""
                )
            return f"Error generating surf conditions: {error_msg}", ""

    def get_one_sentence_summary(
        self, beach_name: str, surf_data: dict, selected_date: str = None
    ) -> str:
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
                selected_date=selected_date or "today",
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite", contents=prompt
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print("⚠️ Gemini API rate limit exceeded. Check your quota at https://console.cloud.google.com/apis/dashboard")
                return "⚠️ API rate limit exceeded. Please check your Google Cloud Console for quota usage."
            return f"Error generating summary: {error_msg}"

    def _format_surf_data(self, surf_data: dict) -> str:
        """
        Format surf data into a readable string for the AI prompt.

        Args:
            surf_data: Dictionary containing surf data from Stormglass API

        Returns:
            Formatted string of surf data
        """
        try:
            if "error" in surf_data:
                return f"Error retrieving surf data: {surf_data['error']}"

            # Handle Stormglass API data structure
            if "data" in surf_data and "hours" in surf_data["data"]:
                # This is raw Stormglass data with nested structure
                hours_data = surf_data["data"]["hours"]
            elif "hours" in surf_data:
                # This is Stormglass data with direct hours structure
                hours_data = surf_data["hours"]
            else:
                # No hours data found
                return "No surf data available for this location and date."

            if not hours_data:
                return "No surf data available for this location and date."

            # Get current conditions (first hour)
            current_hour = hours_data[0]

            # Convert metric to imperial units
            wave_height_m = current_hour.get("waveHeight", {}).get("noaa", 0)
            wave_height_ft = (
                round(float(wave_height_m) * 3.28084, 1)
                if wave_height_m != "N/A" and wave_height_m != 0
                else "N/A"
            )

            wind_speed_ms = current_hour.get("windSpeed", {}).get("noaa", 0)
            wind_speed_mph = (
                round(float(wind_speed_ms) * 2.23694, 1)
                if wind_speed_ms != "N/A" and wind_speed_ms != 0
                else "N/A"
            )

            water_temp_c = current_hour.get("waterTemperature", {}).get("noaa", 0)
            water_temp_f = (
                round((float(water_temp_c) * 9 / 5) + 32, 1)
                if water_temp_c != "N/A" and water_temp_c != 0
                else "N/A"
            )

            air_temp_c = current_hour.get("airTemperature", {}).get("noaa", 0)
            air_temp_f = (
                round((float(air_temp_c) * 9 / 5) + 32, 1)
                if air_temp_c != "N/A" and air_temp_c != 0
                else "N/A"
            )

            visibility_km = current_hour.get("visibility", {}).get("noaa", 0)
            visibility_mi = (
                round(float(visibility_km) * 0.621371, 1)
                if visibility_km != "N/A" and visibility_km != 0
                else "N/A"
            )

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
                time_str = hour.get("time", "N/A")[:16] if hour.get("time") else "N/A"

                # Convert hourly data to imperial units
                hour_wave_height_m = hour.get("waveHeight", {}).get("noaa", 0)
                hour_wave_height_ft = (
                    round(float(hour_wave_height_m) * 3.28084, 1)
                    if hour_wave_height_m != "N/A" and hour_wave_height_m != 0
                    else "N/A"
                )

                hour_wind_speed_ms = hour.get("windSpeed", {}).get("noaa", 0)
                hour_wind_speed_mph = (
                    round(float(hour_wind_speed_ms) * 2.23694, 1)
                    if hour_wind_speed_ms != "N/A" and hour_wind_speed_ms != 0
                    else "N/A"
                )

                hour_water_temp_c = hour.get("waterTemperature", {}).get("noaa", 0)
                hour_water_temp_f = (
                    round((float(hour_water_temp_c) * 9 / 5) + 32, 1)
                    if hour_water_temp_c != "N/A" and hour_water_temp_c != 0
                    else "N/A"
                )

                hour_air_temp_c = hour.get("airTemperature", {}).get("noaa", 0)
                hour_air_temp_f = (
                    round((float(hour_air_temp_c) * 9 / 5) + 32, 1)
                    if hour_air_temp_c != "N/A" and hour_air_temp_c != 0
                    else "N/A"
                )

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

    def parse_best_times_from_analysis(self, ai_analysis_text: str) -> List[Dict]:
        """
        Parse best surf times from AI analysis text.

        Args:
            ai_analysis_text: The full AI analysis text containing best times section

        Returns:
            List of dictionaries with best times data
        """
        try:
            # Find the "Best Time to Surf" section
            # Format can be:
            # "2.  **Best Time to Surf on 2026-01-05:** 12:00 PM - 1:00 PM\n    *   **Rating:**..."
            # OR "2.  **Best Time to Surf on 2026-01-07:**\n    *   The time range: **8:00 AM - 9:00 AM**\n    ..."
            # Find the entire section including the header line
            section_match = re.search(
                r"Best Time to Surf.*?:\*\*(.*?)(?=\n\s*3\.\s+\*\*)",
                ai_analysis_text,
                re.DOTALL | re.IGNORECASE,
            )
            if not section_match:
                return []
            
            # Get the full section including header line
            full_section = section_match.group(0)  # Includes the header
            section = section_match.group(1)  # Content after header
            
            # Extract time - check if it's on the header line first
            # Format 1: "Best Time to Surf on 2026-01-05:** 12:00 PM - 1:00 PM"
            time_match = re.search(
                r":\*\*\s*([0-9]{1,2}:[0-9]{2}\s*[AP]M\s*[-–—]\s*[0-9]{1,2}:[0-9]{2}\s*[AP]M)",
                full_section,
                re.IGNORECASE,
            )
            if not time_match:
                # Format 2: "The time range: **8:00 AM - 9:00 AM**"
                time_match = re.search(
                    r"time range:\s*\*\*([0-9]{1,2}:[0-9]{2}\s*[AP]M\s*[-–—]\s*[0-9]{1,2}:[0-9]{2}\s*[AP]M)\*\*",
                    full_section,
                    re.IGNORECASE,
                )
            time_str = time_match.group(1).strip() if time_match else None
            
            # Rating: Handle "**Rating:** 45/100" or "Rating: **70/100**"
            rating_match = re.search(r"\*\*Rating:\*\*\s*(\d+)/100|\*\*Rating:\*\*\s*(\d+)|Rating:\s*\*\*(\d+)/100\*\*", section, re.IGNORECASE)
            rating = int(rating_match.group(1) or rating_match.group(2) or rating_match.group(3)) if rating_match else None
            
            # Wave height: Handle "**Wave Height:** 5.4-5.2 ft" or "Wave height: **4.0-4.1ft**"
            wave_match = re.search(r"\*\*Wave [Hh]eight:\*\*\s*([0-9.]+[-–—][0-9.]+\s*ft)|Wave height:\s*\*\*([0-9.]+[-–—][0-9.]+ft)\*\*", section, re.IGNORECASE)
            wave_height_range = (wave_match.group(1) or wave_match.group(2)).strip() if wave_match else None
            
            # Period: Handle "**Wave Period:** 10s" or "Wave period: **11s**"
            period_match = re.search(r"\*\*Wave [Pp]eriod:\*\*\s*(\d+)s|Wave period:\s*\*\*(\d+)s\*\*", section, re.IGNORECASE)
            period = int(period_match.group(1) or period_match.group(2)) if period_match else None
            
            # Wind speed: Handle "**Wind Speed:** 8.4-7.9 mph" or "Wind speed: **3.9-4.1 mph**"
            wind_match = re.search(r"\*\*Wind [Ss]peed:\*\*\s*([0-9.]+[-–—][0-9.]+\s*mph)|Wind speed:\s*\*\*([0-9.]+[-–—][0-9.]+ mph)\*\*", section, re.IGNORECASE)
            wind_speed_range = (wind_match.group(1) or wind_match.group(2)).strip() if wind_match else None
            
            # Explanation: "Explanation: [text until next section]"
            explanation_match = re.search(
                r"Explanation:\s*(.+?)(?=\n\s*\*\s*\*\*|$)",
                section,
                re.DOTALL | re.IGNORECASE,
            )
            reason = explanation_match.group(1).strip() if explanation_match else None
            
            # Clean up explanation text
            if reason:
                reason = re.sub(r"\*\*", "", reason)  # Remove bold markers
                reason = re.sub(r"\*", "", reason)  # Remove italic markers
                reason = re.sub(r"[ \t]+", " ", reason)  # Normalize spaces
                reason = re.sub(r"\n[ \t]*\n+", "\n\n", reason)  # Normalize newlines
                reason = reason.strip()
            
            # Only return if we have at least a time
            if time_str:
                return [{
                    "time": time_str,
                    "rating": rating,
                    "wave_height_range": wave_height_range,
                    "period": period,
                    "wind_speed_range": wind_speed_range,
                    "reason": reason,
                }]
            
            return []
            
        except Exception as e:
            print(f"Error parsing best times from AI analysis: {e}")
            import traceback
            traceback.print_exc()
            return []
