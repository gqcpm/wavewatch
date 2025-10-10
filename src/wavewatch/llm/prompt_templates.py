"""
Prompt templates for the WaveWatch application.
"""

SURF_CONDITIONS_PROMPT = """Based on the real-time surf data provided below for {surf_beach}, provide a focused surf analysis.

REAL SURF DATA:
{surf_data}

Please provide ONLY the following analysis:
1. **Overall Surf Rating** (1-10) for today with brief reasoning
2. **Best Times to Surf** today based on the hourly data trends
3. **Specific Recommendations** for surfers (board choice, skill level, etc.)
4. **Notable Changes** in conditions throughout the day

Keep it concise and actionable. Skip basic metrics since they're already displayed."""
