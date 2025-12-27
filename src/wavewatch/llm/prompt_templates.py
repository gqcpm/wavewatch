"""
Prompt templates for the WaveWatch application.
"""

ONE_SENTENCE_SUMMARY_PROMPT = """Based on these surf conditions, provide a single sentence assessment of the surf quality at {beach_name} on {selected_date}.

{formatted_conditions}

Format your response as: "[Quality] surf conditions on {selected_date} at {beach_name} because of [main factor]"

Examples:
- "Poor surf conditions on October 19th at Pleasure Point because of 10mph onshore winds"
- "Good surf conditions on October 20th at Pipeline because of clean 4ft waves and light offshore winds"
- "Fair surf conditions on October 21st at Scripps because of small 2ft waves but clean conditions"

Respond with only the single sentence assessment:"""

IDEAL_CONDITIONS_EXTRACTION_PROMPT = """Using your knowledge of surf breaks and forecasting, create a comprehensive guide to the ideal conditions for {beach_name}.

{search_results}

Your task is to use your general knowledge about this surf break (or similar breaks if you don't have specific knowledge) and create a detailed guide to the ideal conditions for {beach_name}. Format your response as a structured guide similar to the following example:

Here are the ideal conditions for {beach_name}:

1. Swell Direction & Period
   - Ideal Direction: [Primary preferred swell directions with explanation of why they work, e.g., "South (S) to Southwest (SSW) groundswells. These swells aim directly into the point, creating the longest, cleanest lines."]
   - Secondary Option: [Alternative swell directions that also work, if mentioned, e.g., "Large West (W) or Northwest (NW) winter swells. While these can work, they may need to wrap around the point."]
   - Period: [Optimal period range with explanation, e.g., "Long-period swells (12–16+ seconds) are best for the wave to link up and provide long rides."]

2. Wind Conditions
   - Offshore Wind: [Preferred offshore wind directions with explanation, e.g., "Northwest (NW) to Northeast (NE). Because the point faces south/southeast, a NW wind blows from behind the cliffs, grooming the wave faces and keeping them glassy."]
   - Avoid: [Wind conditions to avoid, e.g., "Strong South (S) or Southwest (SW) winds, which blow directly onshore and turn the lineup into a choppy mess."]

3. Tide Conditions
   - Best for Surfing: [Optimal tide range with explanation, e.g., "Low to Mid-tide (incoming). A rising tide from 2.0ft to 4.5ft is generally considered the sweet spot where the reefs have enough water to break smoothly without being too shallow."]
   - The Danger Zone: [Tide conditions to avoid, if any, e.g., "Avoid a High Tide (above 5ft), especially during a big swell. Because the point is backed by steep cliffs with no beach, the waves can surge directly into the rocks."]

4. Break-Specific Guide (if multiple spots/peaks are mentioned)
   - [If the break has multiple peaks or sections, list them with their characteristics, e.g., "First Peak: The main takeoff zone; can handle the most size. Second Peak: A softer, slower wave ideal for longboards."]

5. Best Time of Year (if mentioned)
   - [Seasonal information, e.g., "Summer (June – Sept): Best for consistency. Autumn (Oct – Nov): Often brings the glassiest days with offshore winds."]

6. Local Knowledge & Tips
   - [Any unique local factors, safety considerations, crowd information, or pro tips, e.g., "Pleasure Point is one of the most crowded lineups. If you aren't a local or a high-level surfer, consider moving further inside where the waves are more forgiving."]

Be thorough and detailed. Include explanations for WHY certain conditions are ideal, not just what they are. 

Use your knowledge of:
- The specific break {beach_name} if you know it
- Similar breaks with similar characteristics (point breaks, beach breaks, reef breaks)
- General principles of swell direction, period, tide, and wind for different break types
- Typical conditions for well-known surf spots in the same region or with similar names

Always provide a useful, comprehensive guide. If you don't have specific knowledge about {beach_name}, infer reasonable ideal conditions based on the break name, location clues, and general surf forecasting principles. Focus on creating a guide that a surfer could use to understand what makes this break work best."""

CONDITIONS_COMPARISON_PROMPT = """Act as an expert surf forecaster for {surf_beach}.

1. **Ideal Conditions for {surf_beach}:**
{ideal_conditions}

2. **Current NOAA Data** (for {selected_date}):
{surf_data}

Task:
A. **Comparison**: Compare the current NOAA data against the Ideal Conditions above. Specifically identify:
   - Which current conditions align with the ideal conditions
   - Which current conditions deviate from ideal and how significantly
   - Any dangerous conditions mentioned in the ideal conditions guide that are present in the current data

B. **Analysis**: Provide ONLY the following analysis:
1. **Overall Surf Rating** (1-100) for {selected_date} with brief reasoning that references how current conditions compare to the ideal conditions
2. **Best Time to Surf** on {selected_date} - Identify and provide details for ONLY the single best time period:
   - The time range (e.g., "6:00 AM - 7:00 AM" or "11:00 AM - 12:00 PM") - MUST be exactly 1 hour or less
   - A rating from 1-100 for that time period
   - The range of wave height in feet (e.g., "4.2-4.8ft" or "4.5ft")
   - The wave period rounded to the nearest whole number in seconds (e.g., "14s")
   - The range of wind speed in mph (e.g., "0.6-1.2mph" or "2.6mph")
   - An explanation formatted exactly as follows:
     Explanation: [detailed, in-depth explanation of why this is the optimal time to surf. Specifically cite which conditions (tide/wind/swell) align with the Ideal Conditions above and compare them to the current NOAA data. Note any conditions that may make the session less than ideal or even dangerous, based on the ideal conditions guide. Consider all factors like wave quality, wind conditions, tide, period, consistency, and any other relevant factors that make it ideal compared to the rest of the day]
3. **Specific Recommendations** for surfers (board choice, skill level, etc.) based on how current conditions compare to ideal
4. **Notable Changes** in conditions throughout {selected_date}

Keep it concise and actionable. Skip basic metrics since they're already displayed. Provide ONLY ONE best time period - the single optimal window for surfing. Always reference the ideal conditions guide when explaining ratings and recommendations."""
