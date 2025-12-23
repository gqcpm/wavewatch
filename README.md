# WaveWatch 🏄‍♂️

A full-stack surf forecasting application that provides surf conditions for any beach using Google Gemini AI.

## Features

- Enter any surf beach name (e.g., "Pleasure Point", "Malibu", "Pipeline")
- Get AI-generated surf condition summaries
- Real-time surf data from Stormglass API
- Interactive charts and visualizations
- MongoDB caching for faster responses
- Clean, modern React interface

## Setup

1. **Install dependencies:**
   ```bash
   ./setup.sh
   ```
   Or manually:
   ```bash
   pip install -r requirements.txt
   cd src/wavewatch/ui/client && npm install
   cd ../server && npm install
   ```

2. **Set up your environment:**
   - Create a `.env` file in the project root
   - Add your API keys:
     - `GEMINI_API_KEY=your_api_key_here`
     - `STORMGLASS_API_KEY=your_api_key_here`
     - `MONGODB_URI=your_mongodb_uri` (optional)
   - Get your API keys from:
     - [Google AI Studio](https://makersuite.google.com/app/apikey)
     - [Stormglass](https://stormglass.io)

3. **Run the full stack application:**
   ```bash
   ./setup.sh
   ```
   Or manually start each service:
   ```bash
   # Terminal 1 - FastAPI backend
   python3 surf_api.py
   
   # Terminal 2 - Express/MongoDB server
   cd src/wavewatch/ui/server && npm start
   
   # Terminal 3 - React frontend
   cd src/wavewatch/ui/client && npm start
   ```

## Usage

1. Open http://localhost:3000 in your browser
2. Navigate to the Forecast page
3. Enter a beach name and select a date
4. Click "Get Forecast" to see AI-generated surf conditions

## Example Beaches

- Pleasure Point (Santa Cruz, CA)
- Malibu (Los Angeles, CA)
- Pipeline (Oahu, HI)
- Trestles (San Clemente, CA)
- Mavericks (Half Moon Bay, CA)

## Requirements

- Python 3.7+
- Node.js 16+
- Google Generative AI library
- FastAPI
- React
- MongoDB (optional, for caching)
- Valid Gemini API key
- Valid Stormglass API key
