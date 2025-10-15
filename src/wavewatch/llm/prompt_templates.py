"""
Prompt templates for the WaveWatch application.
"""

SURF_CONDITIONS_PROMPT = """Based on the real-time surf data provided below for {surf_beach} on {selected_date}, provide a focused surf analysis.

REAL SURF DATA:
{surf_data}

Please provide ONLY the following analysis:
1. **Overall Surf Rating** (1-10) for {selected_date} with brief reasoning
2. **Best Times to Surf** on {selected_date} based on the hourly data trends
3. **Specific Recommendations** for surfers (board choice, skill level, etc.)
4. **Notable Changes** in conditions throughout {selected_date}

Keep it concise and actionable. Skip basic metrics since they're already displayed."""

ONE_SENTENCE_SUMMARY_PROMPT = """Based on these surf conditions, provide a single sentence assessment of the surf quality at {beach_name} on {selected_date}. 

{formatted_conditions}

Format your response as: "[Quality] surf conditions on {selected_date} at {beach_name} because of [main factor]"

Examples:
- "Poor surf conditions on October 19th at Pleasure Point because of 15mph onshore winds"
- "Good surf conditions on October 20th at Pipeline because of clean 4ft waves and light offshore winds"
- "Fair surf conditions on October 21st at Scripps because of small 2ft waves but clean conditions"

Respond with only the single sentence assessment:"""
