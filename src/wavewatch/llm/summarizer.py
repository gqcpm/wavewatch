"""
LLM summarizer using Google Gemini for surf condition analysis.
"""

import google.generativeai as genai
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
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def get_surf_conditions(self, surf_beach: str) -> str:
        """
        Get surf conditions summary for a specific beach.
        
        Args:
            surf_beach: Name of the surf beach/break
            
        Returns:
            String containing surf conditions summary
        """
        try:
            prompt = SURF_CONDITIONS_PROMPT.format(surf_beach=surf_beach)
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating surf conditions: {str(e)}"
