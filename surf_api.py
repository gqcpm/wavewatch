#!/usr/bin/env python3
"""
FastAPI wrapper for WaveWatch surf data API
This provides a REST API endpoint for the React frontend to consume
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from wavewatch.api.data_fetcher import StormglassDataFetcher
from wavewatch.llm.summarizer import SurfSummarizer
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="WaveWatch API", version="1.0.0")

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_fetcher = StormglassDataFetcher()
summarizer = SurfSummarizer()

@app.get("/")
async def root():
    return {"message": "🌊 WaveWatch API is running!", "version": "1.0.0"}

@app.get("/api/surf/{beach_name}/{date}")
async def get_surf_data(beach_name: str, date: str):
    """
    Get surf data for a specific beach and date
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Fetch surf data using existing data fetcher
        surf_data_result = data_fetcher.fetch_surf_data(beach_name, date)
        
        # Debug: Check what surf_data contains
        print(f"DEBUG: surf_data_result type: {type(surf_data_result)}")
        print(f"DEBUG: surf_data_result keys: {surf_data_result.keys() if isinstance(surf_data_result, dict) else 'Not a dict'}")
        
        if isinstance(surf_data_result, str):
            raise HTTPException(status_code=404, detail=surf_data_result)
        
        if 'error' in surf_data_result:
            raise HTTPException(status_code=404, detail=surf_data_result['error'])
        
        # Extract the actual surf data for AI analysis
        surf_data_for_ai = surf_data_result.get('data', {})
        
        # Get current conditions
        current_conditions = data_fetcher.get_current_conditions(beach_name, date)
        print(f"DEBUG: current_conditions type: {type(current_conditions)}")
        print(f"DEBUG: current_conditions content: {current_conditions}")
        if isinstance(current_conditions, str):
            current_conditions = {"error": current_conditions}
        
        # Get hourly forecast
        hourly_forecast = data_fetcher.get_hourly_conditions(beach_name, date)
        print(f"DEBUG: hourly_forecast type: {type(hourly_forecast)}")
        print(f"DEBUG: hourly_forecast length: {len(hourly_forecast) if isinstance(hourly_forecast, (list, dict)) else 'Not list/dict'}")
        if isinstance(hourly_forecast, str):
            hourly_forecast = []
        
        # Get best surf times
        best_surf_times_result = data_fetcher.get_best_surf_times(beach_name, date)
        print(f"DEBUG: best_surf_times_result type: {type(best_surf_times_result)}")
        print(f"DEBUG: best_surf_times_result content: {best_surf_times_result}")
        if isinstance(best_surf_times_result, str):
            best_surf_times = []
        elif 'error' in best_surf_times_result:
            best_surf_times = []
        else:
            best_surf_times = best_surf_times_result.get('best_times', [])
        
        print(f"DEBUG: best_surf_times final: {best_surf_times}")
        
        # Check MongoDB cache first for AI responses
        try:
            import requests
            cache_response = requests.get(f"http://localhost:5001/api/surf/{beach_name}/{date}", timeout=2)
            if cache_response.status_code == 200 and cache_response.json():
                cached_data = cache_response.json()
                print("📦 Using cached AI responses from MongoDB")
                ai_analysis = cached_data.get('ai_analysis', {}).get('text', 'No cached analysis')
                one_sentence_summary = cached_data.get('one_sentence_summary', 'No cached summary')
            else:
                # Generate new AI analysis
                ai_analysis_text = summarizer.get_surf_conditions(beach_name, surf_data_for_ai, date)
                print(f"DEBUG: AI analysis text: {ai_analysis_text}")
                
                one_sentence_summary = summarizer.get_one_sentence_summary(beach_name, surf_data_for_ai, date)
                print(f"DEBUG: One sentence summary: {one_sentence_summary}")
                
                ai_analysis = ai_analysis_text
                
                # Cache the response in MongoDB
                cache_data = {
                    "beach_name": beach_name,
                    "date": date,
                    "coordinates": current_conditions.get('coordinates', {}),
                    "current_conditions": current_conditions.get('current_conditions', {}),
                    "hourly_conditions": hourly_forecast.get('hourly_conditions', []),
                    "best_surf_times": best_surf_times,
                    "ai_analysis": {
                        "text": ai_analysis_text,
                        "overall_rating": "N/A",
                        "best_times": "N/A", 
                        "recommendations": "N/A",
                        "notable_changes": "N/A"
                    },
                    "one_sentence_summary": one_sentence_summary
                }
                
                try:
                    cache_save_response = requests.post("http://localhost:5001/api/surf", json=cache_data)
                    if cache_save_response.status_code == 200:
                        print("💾 Cached AI responses in MongoDB")
                except Exception as e:
                    print(f"⚠️ Could not cache in MongoDB: {e}")
        except Exception as e:
            print(f"Warning: Could not check MongoDB cache: {e}")
            # Generate new AI analysis
            ai_analysis_text = summarizer.get_surf_conditions(beach_name, surf_data_for_ai, date)
            print(f"DEBUG: AI analysis text: {ai_analysis_text}")
            
            one_sentence_summary = summarizer.get_one_sentence_summary(beach_name, surf_data_for_ai, date)
            print(f"DEBUG: One sentence summary: {one_sentence_summary}")
            
            ai_analysis = ai_analysis_text
        
        
        # Format response for React frontend
        # Variables already defined above for caching
        
        response = {
            "beachName": beach_name,
            "date": date,
            "currentConditions": current_conditions.get('current_conditions', {}) if isinstance(current_conditions, dict) else {},
            "hourlyForecast": hourly_forecast,
            "bestSurfTimes": best_surf_times,
            "aiAnalysis": ai_analysis,
            "oneSentenceSummary": one_sentence_summary
        }
        
        print(f"DEBUG: Final response keys: {response.keys()}")
        print(f"DEBUG: currentConditions keys: {current_conditions.keys() if isinstance(current_conditions, dict) else 'Not dict'}")
        print(f"DEBUG: bestSurfTimes length: {len(best_surf_times) if isinstance(best_surf_times, list) else 'Not list'}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching surf data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/beaches")
async def get_available_beaches():
    """
    Get list of available beaches
    """
    return {
        "beaches": list(data_fetcher.beach_coordinates.keys())
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("🌊 Starting WaveWatch API server...")
    print("📡 API will be available at: http://localhost:8001")
    print("📚 API docs available at: http://localhost:8001/docs")
    print("🔗 React frontend should connect to: http://localhost:8001")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
