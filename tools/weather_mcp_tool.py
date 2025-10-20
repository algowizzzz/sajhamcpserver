"""
Weather MCP Tool implementation
Provides weather information using wttr.in API
"""
import requests
from typing import Dict, Any
from .base_mcp_tool import BaseMCPTool


class WeatherMCPTool(BaseMCPTool):
    """MCP Tool for Weather information"""

    def _initialize(self):
        """Initialize Weather tool components"""
        self.base_url = "https://wttr.in"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MCP-Weather-Tool/1.0'
        })

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Weather tool calls"""
        try:
            # Check rate limit
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            # Map method names to functions
            tool_methods = {
                "get_current_weather": self._get_current_weather,
                "get_forecast": self._get_forecast,
                "get_weather_by_coordinates": self._get_weather_by_coordinates,
                "get_moon_phase": self._get_moon_phase,
            }

            # Execute method
            if tool_name in tool_methods:
                result = tool_methods[tool_name](arguments)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            # Record call and return
            self.record_call(tool_name, arguments, result=result)
            return result

        except Exception as e:
            error_msg = str(e)
            self.record_call(tool_name, arguments, error=error_msg)
            return {"error": error_msg, "status": 500}

    def _get_current_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current weather for a location"""
        location = params.get('location', '')
        units = params.get('units', 'metric')  # metric or imperial
        
        if not location:
            return {"error": "Location is required"}
        
        try:
            # Format: wttr.in/{location}?format=j1 for JSON
            url = f"{self.base_url}/{location}"
            response = self.session.get(url, params={'format': 'j1'})
            
            if response.status_code != 200:
                return {"error": f"Failed to fetch weather data: {response.status_code}"}
            
            data = response.json()
            current = data.get('current_condition', [{}])[0]
            location_info = data.get('nearest_area', [{}])[0]
            
            # Parse temperature based on units
            if units == 'imperial':
                temp = current.get('temp_F', 'N/A')
                temp_unit = '°F'
                feels_like = current.get('FeelsLikeF', 'N/A')
            else:
                temp = current.get('temp_C', 'N/A')
                temp_unit = '°C'
                feels_like = current.get('FeelsLikeC', 'N/A')
            
            return {
                "location": {
                    "name": location_info.get('areaName', [{}])[0].get('value', location),
                    "region": location_info.get('region', [{}])[0].get('value', 'N/A'),
                    "country": location_info.get('country', [{}])[0].get('value', 'N/A'),
                    "latitude": location_info.get('latitude', 'N/A'),
                    "longitude": location_info.get('longitude', 'N/A')
                },
                "current": {
                    "temperature": f"{temp}{temp_unit}",
                    "feels_like": f"{feels_like}{temp_unit}",
                    "description": current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                    "humidity": f"{current.get('humidity', 'N/A')}%",
                    "wind_speed": f"{current.get('windspeedKmph', 'N/A')} km/h",
                    "wind_direction": current.get('winddir16Point', 'N/A'),
                    "pressure": f"{current.get('pressure', 'N/A')} mb",
                    "visibility": f"{current.get('visibility', 'N/A')} km",
                    "uv_index": current.get('uvIndex', 'N/A'),
                    "cloud_cover": f"{current.get('cloudcover', 'N/A')}%",
                    "observation_time": current.get('observation_time', 'N/A')
                },
                "units": units
            }
        except Exception as e:
            return {"error": f"Failed to get weather: {str(e)}"}

    def _get_forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather forecast for a location"""
        location = params.get('location', '')
        days = params.get('days', 3)  # Number of days (1-3)
        units = params.get('units', 'metric')
        
        if not location:
            return {"error": "Location is required"}
        
        if days < 1 or days > 3:
            days = 3
        
        try:
            url = f"{self.base_url}/{location}"
            response = self.session.get(url, params={'format': 'j1'})
            
            if response.status_code != 200:
                return {"error": f"Failed to fetch forecast: {response.status_code}"}
            
            data = response.json()
            weather_data = data.get('weather', [])
            location_info = data.get('nearest_area', [{}])[0]
            
            forecast = []
            for day_data in weather_data[:days]:
                day_forecast = {
                    "date": day_data.get('date', 'N/A'),
                    "max_temp": f"{day_data.get('maxtempC' if units == 'metric' else 'maxtempF', 'N/A')}{'°C' if units == 'metric' else '°F'}",
                    "min_temp": f"{day_data.get('mintempC' if units == 'metric' else 'mintempF', 'N/A')}{'°C' if units == 'metric' else '°F'}",
                    "avg_temp": f"{day_data.get('avgtempC' if units == 'metric' else 'avgtempF', 'N/A')}{'°C' if units == 'metric' else '°F'}",
                    "sunrise": day_data.get('astronomy', [{}])[0].get('sunrise', 'N/A'),
                    "sunset": day_data.get('astronomy', [{}])[0].get('sunset', 'N/A'),
                    "moon_phase": day_data.get('astronomy', [{}])[0].get('moon_phase', 'N/A'),
                    "total_snow": f"{day_data.get('totalSnow_cm', 0)} cm",
                    "uv_index": day_data.get('uvIndex', 'N/A'),
                    "hourly": []
                }
                
                # Add hourly data (every 3 hours)
                for hour in day_data.get('hourly', []):
                    if int(hour.get('time', '0')) % 300 == 0:  # Every 3 hours
                        day_forecast["hourly"].append({
                            "time": hour.get('time', 'N/A'),
                            "temp": f"{hour.get('tempC' if units == 'metric' else 'tempF', 'N/A')}{'°C' if units == 'metric' else '°F'}",
                            "feels_like": f"{hour.get('FeelsLikeC' if units == 'metric' else 'FeelsLikeF', 'N/A')}{'°C' if units == 'metric' else '°F'}",
                            "description": hour.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                            "chance_of_rain": f"{hour.get('chanceofrain', '0')}%",
                            "chance_of_snow": f"{hour.get('chanceofsnow', '0')}%"
                        })
                
                forecast.append(day_forecast)
            
            return {
                "location": {
                    "name": location_info.get('areaName', [{}])[0].get('value', location),
                    "country": location_info.get('country', [{}])[0].get('value', 'N/A')
                },
                "forecast": forecast,
                "days": len(forecast),
                "units": units
            }
        except Exception as e:
            return {"error": f"Failed to get forecast: {str(e)}"}

    def _get_weather_by_coordinates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather by latitude and longitude"""
        latitude = params.get('latitude')
        longitude = params.get('longitude')
        units = params.get('units', 'metric')
        
        if latitude is None or longitude is None:
            return {"error": "Latitude and longitude are required"}
        
        try:
            # Format coordinates for wttr.in
            location = f"{latitude},{longitude}"
            return self._get_current_weather({
                'location': location,
                'units': units
            })
        except Exception as e:
            return {"error": f"Failed to get weather by coordinates: {str(e)}"}

    def _get_moon_phase(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get moon phase information for a location"""
        location = params.get('location', 'London')  # Default location
        
        try:
            url = f"{self.base_url}/{location}"
            response = self.session.get(url, params={'format': 'j1'})
            
            if response.status_code != 200:
                return {"error": f"Failed to fetch moon data: {response.status_code}"}
            
            data = response.json()
            weather_data = data.get('weather', [{}])[0]
            astronomy = weather_data.get('astronomy', [{}])[0]
            
            return {
                "location": location,
                "date": weather_data.get('date', 'N/A'),
                "moon_phase": astronomy.get('moon_phase', 'N/A'),
                "moon_illumination": f"{astronomy.get('moon_illumination', 'N/A')}%",
                "moonrise": astronomy.get('moonrise', 'N/A'),
                "moonset": astronomy.get('moonset', 'N/A'),
                "sunrise": astronomy.get('sunrise', 'N/A'),
                "sunset": astronomy.get('sunset', 'N/A')
            }
        except Exception as e:
            return {"error": f"Failed to get moon phase: {str(e)}"}

