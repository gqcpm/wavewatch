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
        Generate ideal conditions for a specific break using LLM general knowledge.

        Args:
            beach_name: Name of the beach/break

        Returns:
            Ideal conditions as formatted string
        """
        try:
            prompt = IDEAL_CONDITIONS_EXTRACTION_PROMPT.format(
                beach_name=beach_name, 
                search_results="Use your general knowledge about this surf break. If you don't have specific knowledge about this exact break, use your understanding of similar breaks and general surf forecasting principles."
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
        best_times = []

        try:
            # Look for the "Best Time to Surf" section (singular - only one time)
            # Pattern to match the section that comes after "2. **Best Time to Surf:**" or "Best Time to Surf:**"
            # The new format has the time after the colon: "Best Time to Surf:** 8:00 AM - 9:00 AM"
            best_times_pattern = r"(?i)(?:2\.\s*\*\*best time to surf\*\*:?\s*\*\*|best time to surf:?\s*\*\*)[:\s]*(.*?)(?=\*\*3\.|3\.\s*\*\*|specific recommendations|notable changes|$)"

            # Find the best times section
            best_times_match = re.search(
                best_times_pattern, ai_analysis_text, re.DOTALL
            )

            if not best_times_match:
                # Try alternative patterns (handle variations)
                best_times_pattern = r"(?i)(?:2\.\s*\*\*best times to surf\*\*:|best times to surf:)[:\s]*(.*?)(?=\*\*3\.|3\.\s*\*\*|specific recommendations|notable changes|$)"
                best_times_match = re.search(
                    best_times_pattern, ai_analysis_text, re.DOTALL
                )

            if not best_times_match:
                # Try without colon
                best_times_pattern = r"(?i)best time to surf.*?\n(.*?)(?=\n\*\*|\n\d+\.\s*\*\*|specific recommendations|notable changes|$)"
                best_times_match = re.search(
                    best_times_pattern, ai_analysis_text, re.DOTALL
                )

            if not best_times_match:
                return []

            best_times_section = best_times_match.group(1)

            # The new format has the time at the start after "Best Time to Surf:"
            # Format: "Best Time to Surf: 8:00 AM - 9:00 AM\n    *   Rating: 80/100\n    ..."
            # Since we're only getting ONE time, the entire section is one entry
            # Extract time from the beginning of the section (could be on same line or next line)
            time_at_start = re.search(
                r"^([0-9]{1,2}[:.]?[0-9]{0,2}\s*(?:AM|PM|am|pm)?(?:\s*[-–—]\s*[0-9]{1,2}[:.]?[0-9]{0,2}\s*(?:AM|PM|am|pm))?)[:\s]*",
                best_times_section,
                re.IGNORECASE | re.MULTILINE,
            )

            if time_at_start:
                # Single entry - the entire section
                entries = [best_times_section]
            else:
                # Fallback: try finding time ranges with colons or list format
                time_pattern = r"([0-9]{1,2}[:.]?[0-9]{0,2}\s*(?:AM|PM|am|pm)?(?:\s*[-–—]\s*[0-9]{1,2}[:.]?[0-9]{0,2}\s*(?:AM|PM|am|pm))?):?"
                matches = list(
                    re.finditer(time_pattern, best_times_section, re.IGNORECASE)
                )

                if matches:
                    entries = []
                    for i, match in enumerate(matches):
                        start = match.start()
                        end = (
                            matches[i + 1].start()
                            if i + 1 < len(matches)
                            else len(best_times_section)
                        )
                        entries.append(best_times_section[start:end])
                else:
                    # No time found, use entire section as one entry
                    entries = [best_times_section]

            for entry_text in entries:
                entry_text = entry_text.strip()
                if not entry_text:
                    continue

                # Extract time - in new format it's at the start: "8:00 AM - 9:00 AM\n    *   Rating:..."
                # Or could be: "Best Time to Surf: 8:00 AM - 9:00 AM" (already extracted in section)
                time_match = re.search(
                    r"([0-9]{1,2}[:.]?[0-9]{0,2}\s*(?:AM|PM|am|pm)?(?:\s*[-–—]\s*[0-9]{1,2}[:.]?[0-9]{0,2}\s*(?:AM|PM|am|pm))?)[:\s]*",
                    entry_text,
                    re.IGNORECASE,
                )
                if not time_match:
                    continue

                time_str = time_match.group(1).strip()
                # Clean up time if it has a trailing colon
                if time_str.endswith(":"):
                    time_str = time_str[:-1].strip()

                # Extract rating (1-100) - handle formats like "*   Rating: 80/100" or "Rating: 80"
                rating_match = re.search(
                    r"(?:\*\s*)?(?:rating|score|rated)[:\s]*(\d{1,3})(?:\s*/?\s*100)?",
                    entry_text,
                    re.IGNORECASE,
                )
                rating = int(rating_match.group(1)) if rating_match else None

                # Extract wave height range - handle formats like "*   Wave Height: 5.6-5.7ft"
                wave_match = re.search(
                    r"(?:\*\s*)?wave[^\d]*?(?:height|size)?[:\s]*(\d+\.?\d*\s*[-–—]\s*\d+\.?\d*ft)",
                    entry_text,
                    re.IGNORECASE,
                )
                if not wave_match:
                    # Fallback to single value
                    wave_match = re.search(
                        r"(?:\*\s*)?wave[^\d]*?(?:height|size)?[:\s]*(\d+\.?\d*ft)",
                        entry_text,
                        re.IGNORECASE,
                    )
                wave_height_range = wave_match.group(1).strip() if wave_match else None

                # Extract period - handle formats like "*   Wave Period: 12s"
                period_match = re.search(
                    r"(?:\*\s*)?period[^\d]*?[:\s]*(\d+)\s*s(?:ec(?:ond)?s?)?",
                    entry_text,
                    re.IGNORECASE,
                )
                period = int(period_match.group(1)) if period_match else None

                # Extract wind speed range - handle formats like "*   Wind Speed: 2.9-3.3mph"
                wind_match = re.search(
                    r"(?:\*\s*)?wind[^\d]*?(?:speed)?[:\s]*(\d+\.?\d*\s*[-–—]\s*\d+\.?\d*mph)",
                    entry_text,
                    re.IGNORECASE,
                )
                if not wind_match:
                    # Fallback to single value
                    wind_match = re.search(
                        r"(?:\*\s*)?wind[^\d]*?(?:speed)?[:\s]*(\d+\.?\d*mph)",
                        entry_text,
                        re.IGNORECASE,
                    )
                wind_speed_range = wind_match.group(1).strip() if wind_match else None

                # Extract explanation - look for "Explanation:" marker
                explanation_match = re.search(
                    r"explanation[:\s]+(.+?)(?=\n\s*(?:specific recommendations|notable changes|\d+\.\s*\*\*|$))",
                    entry_text,
                    re.IGNORECASE | re.DOTALL,
                )
                if not explanation_match:
                    # Fallback: find "Explanation:" anywhere and get everything after
                    explanation_match = re.search(
                        r"(?:\*\*)?explanation[:\s]+(.+)",
                        entry_text,
                        re.IGNORECASE | re.DOTALL,
                    )

                if explanation_match:
                    reason = explanation_match.group(1).strip()
                else:
                    # Fallback: try old format with "reason" keyword
                    reason_match = re.search(
                        r"(?:reason|explanation)[:\s]+(.+)",
                        entry_text,
                        re.IGNORECASE | re.DOTALL,
                    )
                    if reason_match:
                        reason = reason_match.group(1).strip()
                    else:
                        reason = None

                # Clean up the explanation text - preserve newlines but clean up markdown
                if reason:
                    # Remove markdown formatting
                    reason = re.sub(r"\*\*", "", reason)
                    reason = re.sub(r"\*", "", reason)
                    # Preserve newlines but normalize multiple spaces within lines
                    # Replace multiple spaces with single space, but keep newlines
                    reason = re.sub(
                        r"[ \t]+", " ", reason
                    )  # Normalize spaces/tabs but keep newlines
                    reason = re.sub(
                        r"\n[ \t]*\n+", "\n\n", reason
                    )  # Normalize multiple newlines to double newline max
                    reason = reason.strip()
                    # Remove trailing colons
                    reason = re.sub(r"[:]\s*$", "", reason).strip()

                # Only add if we have at least a time
                if time_str:
                    best_times.append(
                        {
                            "time": time_str,
                            "rating": rating,
                            "wave_height_range": wave_height_range,
                            "period": period,
                            "wind_speed_range": wind_speed_range,
                            "reason": reason if reason else None,
                        }
                    )

            # Sort by rating (highest first)
            best_times.sort(key=lambda x: x.get("rating", 0) or 0, reverse=True)

            # Return only the single best time
            return best_times[:1] if best_times else []

        except Exception as e:
            print(f"Error parsing best times from AI analysis: {e}")
            import traceback

            traceback.print_exc()
            return []
