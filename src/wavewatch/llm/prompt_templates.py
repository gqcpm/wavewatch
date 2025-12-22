"""
Prompt templates for the WaveWatch application.
"""

SURF_CONDITIONS_PROMPT = """Act as an expert surf forecaster for {surf_beach}.

1. **Break-Specific Requirements:**
{break_specific_conditions}

2. **Current NOAA Data** (for {selected_date}):
{surf_data}

Task:
A. **Comparison**: Compare the current NOAA data against the Break-Specific Requirements above.
B. **Analysis**: Provide ONLY the following analysis:
1. **Overall Surf Rating** (1-100) for {selected_date} with brief reasoning
2. **Best Time to Surf** on {selected_date} - Identify and provide details for ONLY the single best time period:
   - The time range (e.g., "6:00 AM - 7:00 AM" or "11:00 AM - 12:00 PM") - MUST be exactly 1 hour or less
   - A rating from 1-100 for that time period
   - The range of wave height in feet (e.g., "4.2-4.8ft" or "4.5ft")
   - The wave period rounded to the nearest whole number in seconds (e.g., "14s")
   - The range of wind speed in mph (e.g., "0.6-1.2mph" or "2.6mph")
   - An explanation formatted exactly as follows:
     Explanation: [detailed, in-depth explanation of why this is the optimal time to surf. Specifically cite which conditions (tide/wind/swell) align with the Break-Specific Requirements above and compare them to the ideal conditions. Then compare the current NOAA data against those requirements. Note any conditions that may make the session less than ideal or even dangerous, based on the break-specific requirements. Consider all factors like wave quality, wind conditions, tide, period, consistency, and any other relevant factors that make it ideal compared to the rest of the day]
3. **Specific Recommendations** for surfers (board choice, skill level, etc.)
4. **Notable Changes** in conditions throughout {selected_date}

Keep it concise and actionable. Skip basic metrics since they're already displayed. Provide ONLY ONE best time period - the single optimal window for surfing."""

ONE_SENTENCE_SUMMARY_PROMPT = """Based on these surf conditions, provide a single sentence assessment of the surf quality at {beach_name} on {selected_date}.

{formatted_conditions}

Format your response as: "[Quality] surf conditions on {selected_date} at {beach_name} because of [main factor]"

Examples:
- "Poor surf conditions on October 19th at Pleasure Point because of 15mph onshore winds"
- "Good surf conditions on October 20th at Pipeline because of clean 4ft waves and light offshore winds"
- "Fair surf conditions on October 21st at Scripps because of small 2ft waves but clean conditions"

Respond with only the single sentence assessment:"""

BREAK_SPECIFIC_CONDITIONS_EXTRACTION_PROMPT = """Analyze the provided web search results regarding surf conditions at {beach_name}.

WEB SEARCH RESULTS:
{search_results}

Synthesize the information to create a concise, structured list of the most frequently mentioned conditions for this specific break. Focus only on actionable parameters that can be compared against NOAA data.

Format your response as follows:

**Ideal Swell Conditions:**
- Direction: [preferred swell directions, e.g., "W/NW, SW"]
- Period: [optimal period range, e.g., "12+ seconds", "14-18 seconds"]

**Ideal Tide Conditions:**
- Height: [optimal tide height range, e.g., "Mid-tide (3-5ft)", "Low to mid-tide"]
- Notes: [any specific tide-related notes, e.g., "low tide closes out", "high tide too slow"]

**Ideal Wind Conditions:**
- Direction: [preferred wind directions, e.g., "E/SE (offshore)", "Light N"]
- Speed: [optimal wind speed range, e.g., "Light (0-5mph)", "5-10mph"]

**Dangerous/Avoid Conditions:**
- [List any conditions to avoid, e.g., "Strong onshore winds", "Extreme low tide", "High tide closes out"]

**Local Knowledge:**
- [Any unique local factors, e.g., "Foggy in mornings", "Best on incoming tide", "Works best on south swell only", "Currents can be strong"]

If specific information is not found in the search results, indicate "Not specified" for that section. Be concise and focus on the most frequently mentioned and reliable information."""
