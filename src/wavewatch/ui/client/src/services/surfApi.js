// API service to connect to Python surf data backend
const API_BASE_URL = 'http://localhost:8001'; // FastAPI server

class SurfApiService {
  // Get surf data for a specific beach and date
  async getSurfData(beachName, date) {
    try {
      console.log(`🌊 Fetching REAL surf data for ${beachName} on ${date} from ${API_BASE_URL}`);
      
      // Call the FastAPI backend
      const response = await fetch(`${API_BASE_URL}/api/surf/${beachName}/${date}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch surf data');
      }
      
      const data = await response.json();
      console.log('✅ Received REAL surf data from Stormglass API:', data);
      return data;
      
    } catch (error) {
      console.error('❌ Error fetching surf data:', error);
      // Fallback to mock data if API is not available
      console.log('🔄 Falling back to mock data...');
      return this.getMockSurfData(beachName, date);
    }
  }

  // Mock data that matches your Python API structure
  getMockSurfData(beachName, date) {
    return {
      beachName: beachName,
      date: date,
      currentConditions: {
        waveHeight: 3.2,
        wavePeriod: 12,
        waveDirection: 245,
        windSpeed: 8,
        windDirection: 180,
        waterTemperature: 62,
        airTemperature: 68,
        tide: 2.1,
        pressure: 1013,
        humidity: 75,
        visibility: 10,
        cloudCover: 30,
        precipitation: 0
      },
      hourlyForecast: [
        { time: '06:00', waveHeight: 2.8, windSpeed: 6, tide: 1.8, airTemperature: 65 },
        { time: '09:00', waveHeight: 3.2, windSpeed: 8, tide: 2.1, airTemperature: 68 },
        { time: '12:00', waveHeight: 3.5, windSpeed: 10, tide: 2.4, airTemperature: 72 },
        { time: '15:00', waveHeight: 3.8, windSpeed: 12, tide: 2.1, airTemperature: 75 },
        { time: '18:00', waveHeight: 3.2, windSpeed: 9, tide: 1.9, airTemperature: 73 },
        { time: '21:00', waveHeight: 2.9, windSpeed: 7, tide: 1.6, airTemperature: 70 }
      ],
      bestSurfTimes: [
        { time: '06:00', rating: 8, reason: 'Clean conditions, good wave height' },
        { time: '09:00', rating: 9, reason: 'Peak conditions, offshore winds' },
        { time: '12:00', rating: 7, reason: 'Good waves but increasing wind' }
      ],
      aiAnalysis: {
        overallRating: 'Good',
        bestTimes: 'Early morning (6-9 AM) offers the best conditions',
        recommendations: 'Bring a 3/2 wetsuit, consider a longer board for the smaller waves',
        notableChanges: 'Wind picking up in the afternoon, tide dropping after 3 PM'
      },
      oneSentenceSummary: 'Good surf conditions today at ' + beachName + ' with 3-4ft waves and light offshore winds'
    };
  }

  // Method to create a proper API endpoint in your Python backend
  // You would call this from your Python Streamlit app
  async createApiEndpoint() {
    console.log(`
    To create a proper API endpoint, add this to your Python Streamlit app:
    
    import streamlit as st
    from fastapi import FastAPI
    import uvicorn
    
    # Create FastAPI app
    api = FastAPI()
    
    @api.get("/api/surf/{beach_name}/{date}")
    async def get_surf_data(beach_name: str, date: str):
        # Your existing surf data fetching logic here
        # Return JSON data instead of displaying in Streamlit
        return surf_data
    
    # Run both Streamlit and FastAPI
    if __name__ == "__main__":
        # Start FastAPI in background
        uvicorn.run(api, host="0.0.0.0", port=8000)
        # Start Streamlit
        streamlit run streamlit_app.py
    `);
  }
}

export default new SurfApiService();
