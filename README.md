# WaveWatch 🏄‍♂️

A simple Streamlit app that provides surf conditions for any beach using Google Gemini AI.

## Features

- Enter any surf beach name (e.g., "Pleasure Point", "Malibu", "Pipeline")
- Get AI-generated surf condition summaries
- Download conditions reports
- Clean, intuitive interface

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your environment:**
   - Create a `.env` file in the project root
   - Add your Gemini API key: `GEMINI_API_KEY=your_api_key_here`
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## Usage

1. Open the app in your browser
2. Type in a surf beach name
3. Click "Get Surf Conditions"
4. View the AI-generated surf report

## Example Beaches

- Pleasure Point (Santa Cruz, CA)
- Malibu (Los Angeles, CA)
- Pipeline (Oahu, HI)
- Trestles (San Clemente, CA)
- Mavericks (Half Moon Bay, CA)

## Requirements

- Python 3.7+
- Streamlit
- Google Generative AI library
- Valid Gemini API key
