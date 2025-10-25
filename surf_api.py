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
        
        # Initialize variables for data
        current_conditions = {}
        hourly_forecast = []
        best_surf_times = []
        surf_data_for_ai = {}
        
        # Check MongoDB cache first for Stormglass data
        stormglass_cached = False
        try:
            import requests
            stormglass_response = requests.get(f"http://localhost:5001/api/stormglass/{beach_name}/{date}", timeout=2)
            if stormglass_response.status_code == 200 and stormglass_response.json():
                cached_stormglass = stormglass_response.json()
                print("📦 Using cached Stormglass data from MongoDB")
                stormglass_cached = True
                # Use cached data instead of making API calls
                hourly_forecast = cached_stormglass.get('hourly_forecast', [])
                best_surf_times = cached_stormglass.get('best_surf_times', [])
                
                # Extract current conditions from the first hour of hourly_forecast
                if hourly_forecast and len(hourly_forecast) > 0:
                    first_hour = hourly_forecast[0]
                    current_conditions = {
                        'wave_height': first_hour.get('wave_height', 'N/A'),
                        'wave_period': first_hour.get('wave_period', 'N/A'),
                        'wind_speed': first_hour.get('wind_speed', 'N/A'),
                        'water_temperature': first_hour.get('water_temperature', 'N/A'),
                        'air_temperature': first_hour.get('air_temperature', 'N/A'),
                        'tide': first_hour.get('tide', 'N/A')
                    }
                else:
                    current_conditions = {}
                
                # For AI analysis, we still need to fetch the raw data
                surf_data_result = data_fetcher.fetch_surf_data(beach_name, target_date=date)
                if 'error' not in surf_data_result:
                    surf_data_for_ai = surf_data_result.get('data', {})
        except Exception as e:
            print(f"Warning: Could not check Stormglass cache: {e}")
        
        # If no cached data, fetch fresh data from Stormglass API
        if not stormglass_cached:
            print("🌊 Fetching fresh data from Stormglass API")
            # Get current conditions
            current_conditions_result = data_fetcher.get_current_conditions(beach_name, target_date=date)
            # Get hourly forecast
            hourly_forecast_result = data_fetcher.get_hourly_conditions(beach_name, target_date=date)
            # Get best surf times
            best_surf_times_result = data_fetcher.get_best_surf_times(beach_name, target_date=date)
            
            # Extract the data from results
            current_conditions = current_conditions_result.get('current_conditions', {})
            hourly_forecast = hourly_forecast_result.get('hourly_conditions', [])
            best_surf_times = best_surf_times_result.get('best_times', [])
            
            # Get surf data for AI analysis
            surf_data_result = data_fetcher.fetch_surf_data(beach_name, target_date=date)
            if 'error' not in surf_data_result:
                surf_data_for_ai = surf_data_result.get('data', {})
            
            # Cache the Stormglass data
            try:
                # Extract current conditions from the first hour for caching
                current_conditions_for_cache = {}
                if hourly_forecast and len(hourly_forecast) > 0:
                    first_hour = hourly_forecast[0]
                    current_conditions_for_cache = {
                        'wave_height': first_hour.get('wave_height', 'N/A'),
                        'wave_period': first_hour.get('wave_period', 'N/A'),
                        'wind_speed': first_hour.get('wind_speed', 'N/A'),
                        'water_temperature': first_hour.get('water_temperature', 'N/A'),
                        'air_temperature': first_hour.get('air_temperature', 'N/A'),
                        'tide': first_hour.get('tide', 'N/A')
                    }
                
                stormglass_cache_data = {
                    "beach_name": beach_name,
                    "date": date,
                    "current_conditions": current_conditions_for_cache,
                    "hourly_forecast": hourly_forecast,
                    "best_surf_times": best_surf_times
                }
                cache_save_response = requests.post("http://localhost:5001/api/stormglass", json=stormglass_cache_data)
                if cache_save_response.status_code == 200:
                    print("💾 Cached Stormglass data in MongoDB")
            except Exception as e:
                print(f"Warning: Could not cache Stormglass data: {e}")
        
        # Check MongoDB cache for AI responses
        try:
            import requests
            cache_response = requests.get(f"http://localhost:5001/api/surf/{beach_name}/{date}", timeout=2)
            if cache_response.status_code == 200 and cache_response.json():
                cached_data = cache_response.json()
                print(f"DEBUG: Cache response type: {type(cached_data)}")
                print(f"DEBUG: Cache response is array: {isinstance(cached_data, list)}")
                print(f"DEBUG: Cache response keys: {cached_data.keys() if isinstance(cached_data, dict) else 'Not a dict'}")
                
                # Check if cached_data is a dict, not a list
                if isinstance(cached_data, dict):
                    print("📦 Using cached AI responses from MongoDB")
                    ai_analysis = cached_data.get('ai_analysis', {}).get('text', 'No cached analysis')
                    one_sentence_summary = cached_data.get('one_sentence_summary', 'No cached summary')
                else:
                    print(f"Warning: Unexpected cache data type: {type(cached_data)}")
                    raise Exception(f"Cache data is not a dictionary: {type(cached_data)}")
            else:
                # Generate new AI analysis
                ai_analysis_text = summarizer.get_surf_conditions(beach_name, surf_data_for_ai, date)
                one_sentence_summary = summarizer.get_one_sentence_summary(beach_name, surf_data_for_ai, date)
                
                ai_analysis = ai_analysis_text
                
                # Cache the response in MongoDB
                cache_data = {
                    "beach_name": beach_name,
                    "date": date,
                    "current_conditions": current_conditions,
                    "hourly_forecast": hourly_forecast,
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
            one_sentence_summary = summarizer.get_one_sentence_summary(beach_name, surf_data_for_ai, date)
            
            ai_analysis = ai_analysis_text
        
        
        # Format response for React frontend
        # Variables already defined above for caching
        
        response = {
            "beachName": beach_name,
            "date": date,
            "currentConditions": current_conditions if isinstance(current_conditions, dict) else {},
            "hourlyForecast": hourly_forecast,
            "bestSurfTimes": best_surf_times,
            "aiAnalysis": ai_analysis,
            "oneSentenceSummary": one_sentence_summary
        }
        
        
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
