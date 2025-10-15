"""
Stormglass.io API data fetcher for surf conditions.
Fetches swell, wind, tide, and other surf data in a single API call.
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from noaa_coops import Station

# Load environment variables
load_dotenv()

class StormglassDataFetcher:
    """Fetches surf data from Stormglass.io API with caching."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the data fetcher.
        
        Args:
            api_key: Stormglass API key. If None, will try to get from environment.
        """
        if api_key is None:
            api_key = os.getenv('STORMGLASS_API_KEY')
        
        if not api_key:
            raise ValueError("Stormglass API key is required. Set STORMGLASS_API_KEY environment variable or pass api_key parameter.")
        
        self.api_key = api_key
        self.base_url = "https://api.stormglass.io/v2"
        self.cache_file = "surf_data_cache.json"
        self.cache_expiry = 86400  # 24 hours in seconds
        
        # Mapping of beaches to nearest NOAA tide stations
        self.tide_stations = {
            "pleasure point": "9413745",  # Santa Cruz, Monterey Bay, CA
            "malibu": "9410660",         # Los Angeles, CA
            "pipeline": "1612340",       # Honolulu, HI
            "trestles": "9410660",       # Los Angeles, CA (closest)
            "mavericks": "9413450",      # Half Moon Bay, CA
            "huntington beach": "9410660", # Los Angeles, CA
            "venice beach": "9410660",   # Los Angeles, CA
            "manhattan beach": "9410660", # Los Angeles, CA
            "hermosa beach": "9410660",  # Los Angeles, CA
            "redondo beach": "9410660", # Los Angeles, CA
            "el segundo": "9410660",    # Los Angeles, CA
            "scripps": "9410230",       # La Jolla, CA
            "tourmaline": "9410230",    # La Jolla, CA
        }
        
        # Common surf beach coordinates (lat, lng)
        self.beach_coordinates = {
            "pleasure point": (36.9514, -122.0256),
            "malibu": (34.0259, -118.7798),
            "pipeline": (21.6611, -158.0536),
            "trestles": (33.3703, -117.5681),
            "mavericks": (37.4897, -122.4993),
            "huntington beach": (33.6595, -117.9988),
            "venice beach": (33.9850, -118.4695),
            "manhattan beach": (33.8847, -118.4109),
            "hermosa beach": (33.8622, -118.3991),
            "redondo beach": (33.8492, -118.3881),
            "el segundo": (33.9192, -118.4165),
            "torrance beach": (33.8036, -118.3931),
            "palos verdes": (33.7444, -118.3878),
            "rancho palos verdes": (33.7444, -118.3878),
            "san onofre": (33.3703, -117.5681),
            "doheny": (33.4625, -117.7142),
            "salt creek": (33.4625, -117.7142),
            "laguna beach": (33.5427, -117.7854),
            "newport beach": (33.6189, -117.9298),
            "seal beach": (33.7414, -118.1048),
            "long beach": (33.7701, -118.1937),
            "sunset beach": (33.7167, -118.0833),
            "bolsa chica": (33.7414, -118.1048),
            "huntington state beach": (33.6595, -117.9988),
            "crystal cove": (33.5427, -117.7854),
            "corona del mar": (33.6189, -117.9298),
            "balboa": (33.6189, -117.9298),
            "newport pier": (33.6189, -117.9298),
            "blackies": (33.6189, -117.9298),
            "the wedge": (33.6189, -117.9298),
            "salt creek": (33.4625, -117.7142),
            "doheny state beach": (33.4625, -117.7142),
            "san clemente": (33.3703, -117.5681),
            "trestles": (33.3703, -117.5681),
            "san onofre state beach": (33.3703, -117.5681),
            "trails": (33.3703, -117.5681),
            "old man's": (33.3703, -117.5681),
            "church": (33.3703, -117.5681),
            "middles": (33.3703, -117.5681),
            "cottons": (33.3703, -117.5681),
            "upper trestles": (33.3703, -117.5681),
            "lower trestles": (33.3703, -117.5681),
            "uppers": (33.3703, -117.5681),
            "lowers": (33.3703, -117.5681),
            "trestles": (33.3703, -117.5681),
            "san onofre": (33.3703, -117.5681),
            "trails": (33.3703, -117.5681),
            "old man's": (33.3703, -117.5681),
            "church": (33.3703, -117.5681),
            "middles": (33.3703, -117.5681),
            "cottons": (33.3703, -117.5681),
            "upper trestles": (33.3703, -117.5681),
            "lower trestles": (33.3703, -117.5681),
            "uppers": (33.3703, -117.5681),
            "lowers": (33.3703, -117.5681),
            "scripps": (32.8667, -117.2500),
            "tourmaline": (32.8000, -117.2667),
        }
    
    def _load_cache(self) -> Dict:
        """Load cached data from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as file:
                    return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return {}
    
    def _save_cache(self, cache: Dict) -> None:
        """Save data to cache file."""
        try:
            with open(self.cache_file, 'w') as file:
                json.dump(cache, file, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def _get_beach_coordinates(self, beach_name: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a beach name.
        
        Args:
            beach_name: Name of the surf beach
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        # Try exact match first
        beach_key = beach_name.lower().strip()
        if beach_key in self.beach_coordinates:
            return self.beach_coordinates[beach_key]
        
        # Try partial matches
        for key, coords in self.beach_coordinates.items():
            if beach_key in key or key in beach_key:
                return coords
        
        return None
    
    def _get_noaa_tide_data(self, beach_name: str, target_date: str = None) -> Dict:
        """
        Get tide data from NOAA CO-OPS for the nearest tide station.
        
        Args:
            beach_name: Name of the surf beach
            target_date: Target date in YYYY-MM-DD format
            
        Returns:
            Dictionary with tide data or error information
        """
        try:
            # Get the tide station ID for this beach
            station_id = self.tide_stations.get(beach_name.lower())
            if not station_id:
                return {'error': f'No tide station found for {beach_name}'}
            
            # Parse target date or use current date
            if target_date:
                if isinstance(target_date, str):
                    date_obj = datetime.strptime(target_date, '%Y-%m-%d')
                else:
                    date_obj = target_date  # Already a datetime object
            else:
                date_obj = datetime.now()
            
            # Create station object
            station = Station(station_id)
            
            # Get hourly tide data for the day
            # Convert datetime to string format that NOAA CO-OPS expects
            date_str = date_obj.strftime('%Y%m%d')
            tide_data = station.get_data(
                begin_date=date_str,
                end_date=date_str,
                product='hourly_height',
                datum='MLLW',
                units='metric',
                time_zone='gmt'
            )
            
            if tide_data.empty:
                return {'error': 'No tide data available for this date'}
            
            # Convert to our format
            tide_conditions = []
            for index, row in tide_data.iterrows():
                # Convert timestamp to ISO format
                iso_time = index.strftime('%Y-%m-%dT%H:%M:%S+00:00')
                
                tide_conditions.append({
                    'time': iso_time,
                    'tide': round(float(row['hourly_height']) * 3.28084, 2)  # Convert meters to feet
                })
            
            return {
                'tide_conditions': tide_conditions,
                'station_id': station_id,
                'station_name': f'Station {station_id}'
            }
            
        except Exception as e:
            return {'error': f'Error fetching NOAA tide data: {str(e)}'}
    
    def fetch_surf_data(self, beach_name: str, lat: Optional[float] = None, lng: Optional[float] = None, target_date: str = None) -> Dict:
        """
        Fetch surf data for a beach with caching.
        
        Args:
            beach_name: Name of the surf beach
            lat: Latitude (optional, will lookup if not provided)
            lng: Longitude (optional, will lookup if not provided)
            target_date: Target date in YYYY-MM-DD format (optional, defaults to current day)
            
        Returns:
            Dictionary containing surf data or error information
        """
        # Get coordinates
        if lat is None or lng is None:
            coords = self._get_beach_coordinates(beach_name)
            if coords is None:
                return {
                    'error': f'Beach "{beach_name}" not found in database. Please provide coordinates.',
                    'beach_name': beach_name
                }
            lat, lng = coords
        
        # Check cache first
        cache = self._load_cache()
        # Create cache key with date
        date_suffix = f"_{target_date}" if target_date else ""
        cache_key = f"{lat},{lng}{date_suffix}"
        current_time = time.time()
        
        if cache_key in cache:
            cached_data = cache[cache_key]
            if (current_time - cached_data['timestamp']) < self.cache_expiry:
                return {
                    'beach_name': beach_name,
                    'coordinates': {'lat': lat, 'lng': lng},
                    'data': cached_data['data'],
                    'tide_data': cached_data.get('tide_data', {}),
                    'cached': True,
                    'timestamp': cached_data['timestamp']
                }
        
        # Make API call
        try:
            # Single API call with all parameters for the entire day
            url = f"{self.base_url}/weather/point"
            params = {
                'lat': lat,
                'lng': lng,
                'params': ','.join([
                    'waveHeight',      # Wave height
                    'waveDirection',   # Wave direction
                    'wavePeriod',      # Wave period
                    'windSpeed',       # Wind speed
                    'windDirection',   # Wind direction
                    'waterTemperature', # Water temperature
                    'airTemperature',  # Air temperature
                    'pressure',        # Atmospheric pressure
                    'humidity',        # Humidity
                    'visibility',      # Visibility
                    'cloudCover',     # Cloud cover
                    'precipitation',   # Precipitation
                    'seaLevel'        # Sea level (tide equivalent)
                ]),
                'source': 'noaa',  # Use NOAA as primary source
                'start': int((datetime.strptime(target_date, '%Y-%m-%d') if isinstance(target_date, str) else target_date).replace(hour=0, minute=0, second=0).timestamp()) if target_date else int(datetime.now().replace(hour=0, minute=0, second=0).timestamp()),  # Start of target day
                'end': int((datetime.strptime(target_date, '%Y-%m-%d') if isinstance(target_date, str) else target_date).replace(hour=23, minute=59, second=59).timestamp()) if target_date else int(datetime.now().replace(hour=23, minute=59, second=59).timestamp())  # End of target day
            }
            
            headers = {
                'Authorization': self.api_key
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Get NOAA tide data
                tide_data = self._get_noaa_tide_data(beach_name, target_date)
                
                # Cache the data
                cache_data = {
                    'data': data,
                    'tide_data': tide_data,
                    'timestamp': current_time
                }
                cache[cache_key] = cache_data
                self._save_cache(cache)
                
                return {
                    'beach_name': beach_name,
                    'coordinates': {'lat': lat, 'lng': lng},
                    'data': data,
                    'tide_data': tide_data,
                    'cached': False,
                    'timestamp': current_time
                }
            else:
                return {
                    'error': f'API request failed with status {response.status_code}: {response.text}',
                    'beach_name': beach_name,
                    'coordinates': {'lat': lat, 'lng': lng}
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'error': f'Network error: {str(e)}',
                'beach_name': beach_name,
                'coordinates': {'lat': lat, 'lng': lng}
            }
        except Exception as e:
            return {
                'error': f'Unexpected error: {str(e)}',
                'beach_name': beach_name,
                'coordinates': {'lat': lat, 'lng': lng}
            }
    
    def get_hourly_conditions(self, beach_name: str, lat: Optional[float] = None, lng: Optional[float] = None, target_date: str = None) -> Dict:
        """
        Get hourly surf conditions for the entire day.
        
        Args:
            beach_name: Name of the surf beach
            lat: Latitude (optional)
            lng: Longitude (optional)
            
        Returns:
            Dictionary with hourly conditions for the day
        """
        result = self.fetch_surf_data(beach_name, lat, lng, target_date)
        
        if 'error' in result:
            return result
        
        try:
            data = result['data']
            hours = data.get('hours', [])
            
            hourly_conditions = []
            for hour_data in hours:
                # Convert units from metric to imperial
                wave_height_m = hour_data.get('waveHeight', {}).get('noaa', 'N/A')
                wave_height_ft = round(float(wave_height_m) * 3.28084, 1) if wave_height_m != 'N/A' else 'N/A'
                
                wind_speed_ms = hour_data.get('windSpeed', {}).get('noaa', 'N/A')
                wind_speed_mph = round(float(wind_speed_ms) * 2.23694, 1) if wind_speed_ms != 'N/A' else 'N/A'
                
                water_temp_c = hour_data.get('waterTemperature', {}).get('noaa', 'N/A')
                water_temp_f = round(float(water_temp_c) * 9/5 + 32, 1) if water_temp_c != 'N/A' else 'N/A'
                
                air_temp_c = hour_data.get('airTemperature', {}).get('noaa', 'N/A')
                air_temp_f = round(float(air_temp_c) * 9/5 + 32, 1) if air_temp_c != 'N/A' else 'N/A'
                
                visibility_km = hour_data.get('visibility', {}).get('noaa', 'N/A')
                visibility_mi = round(float(visibility_km) * 0.621371, 1) if visibility_km != 'N/A' else 'N/A'
                
                # Get tide data from NOAA CO-OPS if available
                tide_ft = 'N/A'
                if 'tide_data' in result and 'tide_conditions' in result['tide_data']:
                    # Find matching tide data for this hour
                    hour_time = hour_data.get('time', '')
                    for tide_entry in result['tide_data']['tide_conditions']:
                        if tide_entry['time'] == hour_time:
                            tide_ft = tide_entry['tide']
                            break
                
                # Fallback to Stormglass data if NOAA data not available
                if tide_ft == 'N/A':
                    sea_level_m = hour_data.get('seaLevel', {}).get('noaa', 'N/A')
                    
                    if sea_level_m != 'N/A':
                        tide_ft = round(float(sea_level_m) * 3.28084, 1)
                
                hourly_conditions.append({
                    'time': hour_data.get('time', 'N/A'),
                    'wave_height': wave_height_ft,
                    'wave_direction': hour_data.get('waveDirection', {}).get('noaa', 'N/A'),
                    'wave_period': hour_data.get('wavePeriod', {}).get('noaa', 'N/A'),
                    'wind_speed': wind_speed_mph,
                    'wind_direction': hour_data.get('windDirection', {}).get('noaa', 'N/A'),
                    'water_temperature': water_temp_f,
                    'air_temperature': air_temp_f,
                    'pressure': hour_data.get('pressure', {}).get('noaa', 'N/A'),
                    'humidity': hour_data.get('humidity', {}).get('noaa', 'N/A'),
                    'visibility': visibility_mi,
                    'cloud_cover': hour_data.get('cloudCover', {}).get('noaa', 'N/A'),
                    'precipitation': hour_data.get('precipitation', {}).get('noaa', 'N/A'),
                    'tide': tide_ft
                })
            
            return {
                'beach_name': result['beach_name'],
                'coordinates': result['coordinates'],
                'cached': result.get('cached', False),
                'timestamp': result.get('timestamp'),
                'hourly_conditions': hourly_conditions,
                'total_hours': len(hourly_conditions)
            }
        except (KeyError, IndexError, TypeError) as e:
            return {
                'error': f'Error parsing API response: {str(e)}',
                'beach_name': result['beach_name'],
                'coordinates': result['coordinates']
            }
    
    def get_best_surf_times(self, beach_name: str, lat: Optional[float] = None, lng: Optional[float] = None, min_wave_height: float = 2.0, target_date: str = None) -> Dict:
        """
        Get the best surf times for the day based on wave height and conditions.
        
        Args:
            beach_name: Name of the surf beach
            lat: Latitude (optional)
            lng: Longitude (optional)
            min_wave_height: Minimum wave height to consider (default: 2.0 ft)
            
        Returns:
            Dictionary with best surf times and conditions
        """
        result = self.get_hourly_conditions(beach_name, lat, lng)
        
        if 'error' in result:
            return result
        
        try:
            hourly_conditions = result['hourly_conditions']
            best_times = []
            
            for hour in hourly_conditions:
                try:
                    wave_height = float(hour['wave_height']) if hour['wave_height'] != 'N/A' else 0
                    wind_speed = float(hour['wind_speed']) if hour['wind_speed'] != 'N/A' else 0
                    
                    # Score based on wave height and wind conditions
                    if wave_height >= min_wave_height:
                        # Lower wind is better (assuming offshore or light onshore)
                        wind_score = max(0, 20 - wind_speed)  # Max score of 20 for no wind
                        wave_score = min(30, wave_height * 10)  # Max score of 30 for 3+ ft waves
                        total_score = wave_score + wind_score
                        
                        best_times.append({
                            'time': hour['time'],
                            'wave_height': hour['wave_height'],
                            'wave_period': hour['wave_period'],
                            'wind_speed': hour['wind_speed'],
                            'wind_direction': hour['wind_direction'],
                            'water_temperature': hour['water_temperature'],
                            'tide': hour['tide'],
                            'score': total_score
                        })
                except (ValueError, TypeError):
                    continue
            
            # Sort by score (highest first)
            best_times.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                'beach_name': result['beach_name'],
                'coordinates': result['coordinates'],
                'cached': result.get('cached', False),
                'best_times': best_times[:5],  # Top 5 times
                'total_good_hours': len(best_times),
                'min_wave_height': min_wave_height
            }
        except Exception as e:
            return {
                'error': f'Error analyzing surf conditions: {str(e)}',
                'beach_name': result['beach_name'],
                'coordinates': result['coordinates']
            }
    
    def get_current_conditions(self, beach_name: str, lat: Optional[float] = None, lng: Optional[float] = None, target_date: str = None) -> Dict:
        """
        Get current surf conditions in a simplified format.
        
        Args:
            beach_name: Name of the surf beach
            lat: Latitude (optional)
            lng: Longitude (optional)
            
        Returns:
            Dictionary with current conditions
        """
        result = self.fetch_surf_data(beach_name, lat, lng, target_date)
        
        if 'error' in result:
            return result
        
        try:
            data = result['data']
            current_hour = data['hours'][0]  # Get current hour data
            
            # Convert units from metric to imperial
            wave_height_m = current_hour.get('waveHeight', {}).get('noaa', 'N/A')
            wave_height_ft = round(float(wave_height_m) * 3.28084, 1) if wave_height_m != 'N/A' else 'N/A'
            
            wind_speed_ms = current_hour.get('windSpeed', {}).get('noaa', 'N/A')
            wind_speed_mph = round(float(wind_speed_ms) * 2.23694, 1) if wind_speed_ms != 'N/A' else 'N/A'
            
            water_temp_c = current_hour.get('waterTemperature', {}).get('noaa', 'N/A')
            water_temp_f = round(float(water_temp_c) * 9/5 + 32, 1) if water_temp_c != 'N/A' else 'N/A'
            
            air_temp_c = current_hour.get('airTemperature', {}).get('noaa', 'N/A')
            air_temp_f = round(float(air_temp_c) * 9/5 + 32, 1) if air_temp_c != 'N/A' else 'N/A'
            
            visibility_km = current_hour.get('visibility', {}).get('noaa', 'N/A')
            visibility_mi = round(float(visibility_km) * 0.621371, 1) if visibility_km != 'N/A' else 'N/A'
            
            # Get tide data from NOAA CO-OPS if available
            tide_ft = 'N/A'
            if 'tide_data' in result and 'tide_conditions' in result['tide_data']:
                # Find current hour tide data
                current_time = current_hour.get('time', '')
                for tide_entry in result['tide_data']['tide_conditions']:
                    if tide_entry['time'] == current_time:
                        tide_ft = tide_entry['tide']
                        break
            
            # Fallback to Stormglass data if NOAA data not available
            if tide_ft == 'N/A':
                sea_level_m = current_hour.get('seaLevel', {}).get('noaa', 'N/A')
                
                if sea_level_m != 'N/A':
                    tide_ft = round(float(sea_level_m) * 3.28084, 1)
            
            return {
                'beach_name': result['beach_name'],
                'coordinates': result['coordinates'],
                'cached': result.get('cached', False),
                'timestamp': result.get('timestamp'),
                'current_conditions': {
                    'wave_height': wave_height_ft,
                    'wave_direction': current_hour.get('waveDirection', {}).get('noaa', 'N/A'),
                    'wave_period': current_hour.get('wavePeriod', {}).get('noaa', 'N/A'),
                    'wind_speed': wind_speed_mph,
                    'wind_direction': current_hour.get('windDirection', {}).get('noaa', 'N/A'),
                    'water_temperature': water_temp_f,
                    'air_temperature': air_temp_f,
                    'pressure': current_hour.get('pressure', {}).get('noaa', 'N/A'),
                    'humidity': current_hour.get('humidity', {}).get('noaa', 'N/A'),
                    'visibility': visibility_mi,
                    'cloud_cover': current_hour.get('cloudCover', {}).get('noaa', 'N/A'),
                    'precipitation': current_hour.get('precipitation', {}).get('noaa', 'N/A'),
                    'tide': tide_ft
                }
            }
        except (KeyError, IndexError, TypeError) as e:
            return {
                'error': f'Error parsing API response: {str(e)}',
                'beach_name': result['beach_name'],
                'coordinates': result['coordinates']
            }
