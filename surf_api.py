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


from wavewatch.api.data_fetcher import StormglassDataFetcher
from wavewatch.llm.summarizer import SurfSummarizer
from dotenv import load_dotenv
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


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
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

        # Check MongoDB cache first for complete response (industry standard: cache the full resource)
        import requests

        try:
            cache_response = requests.get(
                f"http://localhost:5001/api/surf/{beach_name}/{date}", timeout=2
            )
            if cache_response.status_code == 200:
                cached_data = cache_response.json()
                if cached_data and isinstance(cached_data, dict):
                    print("📦 Using cached complete response from MongoDB")

                    # Get tide data (not cached, fetch fresh as it's separate data source)
                    tide_data = {}
                    try:
                        tide_data = data_fetcher._get_noaa_tide_data(
                            beach_name, target_date=date
                        )
                        if "error" in tide_data:
                            tide_data = {}
                    except Exception as e:
                        tide_data = {}
                        print(f"Error getting tide data: {e}")

                    # Format response from cache
                    ai_analysis_dict = cached_data.get("ai_analysis", {})
                    ai_analysis = (
                        ai_analysis_dict.get("text", "")
                        if isinstance(ai_analysis_dict, dict)
                        else cached_data.get("ai_analysis", "")
                    )

                    # Always re-parse best_surf_times from AI analysis to ensure we have the latest format
                    # This fixes issues with old cached data that might have incorrect parsing
                    best_surf_times = []
                    if ai_analysis:
                        best_surf_times = summarizer.parse_best_times_from_analysis(ai_analysis)
                    # Fallback to cached if parsing fails
                    if not best_surf_times:
                        best_surf_times = cached_data.get("best_surf_times", [])

                    # Handle both hourly_forecast (legacy) and hourly_conditions (schema) field names
                    hourly_forecast = cached_data.get(
                        "hourly_conditions"
                    ) or cached_data.get("hourly_forecast", [])

                    return {
                        "beachName": beach_name,
                        "date": date,
                        "currentConditions": cached_data.get("current_conditions", {}),
                        "hourlyForecast": hourly_forecast,
                        "bestSurfTimes": best_surf_times,
                        "idealConditions": cached_data.get(
                            "ideal_conditions", ""
                        ),
                        "aiAnalysis": ai_analysis,
                        "oneSentenceSummary": cached_data.get(
                            "one_sentence_summary", ""
                        ),
                        "tideData": tide_data,
                    }
        except Exception as e:
            print(f"Warning: Could not check MongoDB cache: {e}")

        # Cache miss - fetch fresh data and generate AI analysis
        print("🌊 Fetching fresh data from Stormglass API")

        # Get current conditions and hourly forecast
        current_conditions_result = data_fetcher.get_current_conditions(
            beach_name, target_date=date
        )
        hourly_forecast_result = data_fetcher.get_hourly_conditions(
            beach_name, target_date=date
        )

        current_conditions = current_conditions_result.get("current_conditions", {})
        hourly_forecast = hourly_forecast_result.get("hourly_conditions", [])

        # Get surf data for AI analysis
        surf_data_result = data_fetcher.fetch_surf_data(beach_name, target_date=date)
        surf_data_for_ai = (
            surf_data_result.get("data", {}) if "error" not in surf_data_result else {}
        )

        # Generate AI analysis
        ai_analysis_text, ideal_conditions = summarizer.get_surf_conditions(
            beach_name, surf_data_for_ai, date
        )
        # Skip one-sentence summary if main analysis failed to save API calls
        one_sentence_summary = ""
        if (
            ai_analysis_text
            and "Error" not in ai_analysis_text
            and "429" not in ai_analysis_text
        ):
            try:
                one_sentence_summary = summarizer.get_one_sentence_summary(
                    beach_name, surf_data_for_ai, date
                )
            except Exception as e:
                print(f"⚠️ Could not generate one-sentence summary: {e}")
                one_sentence_summary = ""
        best_surf_times = summarizer.parse_best_times_from_analysis(ai_analysis_text)

        # Get tide data
        tide_data = {}
        try:
            tide_data = data_fetcher._get_noaa_tide_data(beach_name, target_date=date)
            if "error" in tide_data:
                tide_data = {}
        except Exception as e:
            tide_data = {}
            print(f"Error getting tide data: {e}")

        # Cache complete response in MongoDB (using schema field names)
        cache_data = {
            "beach_name": beach_name,
            "date": date,
            "current_conditions": current_conditions,
            "hourly_conditions": hourly_forecast,  # MongoDB schema uses hourly_conditions
            "best_surf_times": best_surf_times,
            "ideal_conditions": ideal_conditions,
            "ai_analysis": {
                "text": ai_analysis_text,
                "overall_rating": "N/A",
                "best_times": "N/A",
                "recommendations": "N/A",
                "notable_changes": "N/A",
            },
            "one_sentence_summary": one_sentence_summary,
        }

        try:
            cache_save_response = requests.post(
                "http://localhost:5001/api/surf", json=cache_data, timeout=2
            )
            if cache_save_response.status_code == 200:
                print("💾 Cached complete response in MongoDB")
        except Exception as e:
            print(f"⚠️ Could not cache in MongoDB: {e}")

        # Return response
        return {
            "beachName": beach_name,
            "date": date,
            "currentConditions": (
                current_conditions if isinstance(current_conditions, dict) else {}
            ),
            "hourlyForecast": hourly_forecast,
            "bestSurfTimes": best_surf_times,
            "idealConditions": ideal_conditions,
            "aiAnalysis": ai_analysis_text,
            "oneSentenceSummary": one_sentence_summary,
            "tideData": tide_data,
        }

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
    return {"beaches": list(data_fetcher.beach_coordinates.keys())}


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
