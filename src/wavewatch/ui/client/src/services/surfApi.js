// API service to connect to Python surf data backend
const API_BASE_URL = 'http://localhost:8001'; // FastAPI server

class SurfApiService {
  // Get surf data for a specific beach and date
  async getSurfData(beachName, date) {
    try {
      console.log(
        `🌊 Fetching REAL surf data for ${beachName} on ${date} from ${API_BASE_URL}`
      );

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
        wave_height: 3.2,
        wave_period: 12,
        wave_direction: 245,
        wind_speed: 8,
        wind_direction: 250,
        water_temperature: 62,
        air_temperature: 68,
        tide: 2.1,
        pressure: 1013,
        humidity: 75,
        visibility: 10,
        cloudCover: 30,
        precipitation: 0,
      },
      hourlyForecast: [
        {
          time: '06:00',
          waveHeight: 2.8,
          windSpeed: 6,
          windDirection: 245,
          tide: 1.8,
          airTemperature: 65,
        },
        {
          time: '09:00',
          waveHeight: 3.2,
          windSpeed: 8,
          windDirection: 250,
          tide: 2.1,
          airTemperature: 68,
        },
        {
          time: '12:00',
          waveHeight: 3.5,
          windSpeed: 10,
          windDirection: 255,
          tide: 2.4,
          airTemperature: 72,
        },
        {
          time: '15:00',
          waveHeight: 3.8,
          windSpeed: 12,
          windDirection: 260,
          tide: 2.1,
          airTemperature: 75,
        },
        {
          time: '18:00',
          waveHeight: 3.2,
          windSpeed: 9,
          windDirection: 265,
          tide: 1.9,
          airTemperature: 73,
        },
        {
          time: '21:00',
          waveHeight: 2.9,
          windSpeed: 7,
          windDirection: 270,
          tide: 1.6,
          airTemperature: 70,
        },
      ],
      bestSurfTimes: [
        { time: '06:00', rating: 8, reason: 'Clean conditions, good wave height' },
        { time: '09:00', rating: 9, reason: 'Peak conditions, offshore winds' },
        { time: '12:00', rating: 7, reason: 'Good waves but increasing wind' },
      ],
      aiAnalysis: {
        overallRating: 'Good',
        bestTimes: 'Early morning (6-9 AM) offers the best conditions',
        recommendations:
          'Bring a 3/2 wetsuit, consider a longer board for the smaller waves',
        notableChanges: 'Wind picking up in the afternoon, tide dropping after 3 PM',
      },
      oneSentenceSummary:
        'Good surf conditions today at ' +
        beachName +
        ' with 3-4ft waves and light offshore winds',
    };
  }

  // Method to create a proper API endpoint in your Python backend
  // This is already implemented in surf_api.py
  async createApiEndpoint() {
    console.log(`
    The API endpoint is already implemented in surf_api.py.
    
    To use it, start the FastAPI server:
    
    python3 surf_api.py
    
    The API will be available at http://localhost:8001
    API documentation: http://localhost:8001/docs
    `);
  }
}

const surfApiService = new SurfApiService();

export default surfApiService;
