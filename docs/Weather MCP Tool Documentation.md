# Weather MCP Tool Documentation

## Overview
The Weather MCP Tool provides real-time weather information, forecasts, and astronomical data using the wttr.in weather service.

## Configuration
- **No API key required** ✅
- Uses wttr.in free weather API
- Real-time weather data
- Up to 3-day forecasts
- Global coverage

## Available Methods

### 1. get_current_weather
Get current weather conditions for any location.

**Parameters:**
- `location` (required): City name, address, or location
  - Examples: "London", "New York", "Paris", "Tokyo", "San Francisco"
- `units` (default: 'metric'): Temperature units
  - `'metric'`: Celsius, km/h
  - `'imperial'`: Fahrenheit, mph

**Returns:**
- Location information (name, region, country, coordinates)
- Current temperature and "feels like"
- Weather description
- Humidity, wind speed, wind direction
- Atmospheric pressure
- Visibility
- UV index
- Cloud cover
- Observation time

**Example Usage:**
```json
{
  "method": "get_current_weather",
  "arguments": {
    "location": "London",
    "units": "metric"
  }
}
```

**Example Response:**
```json
{
  "location": {
    "name": "London",
    "region": "City of London, Greater London",
    "country": "United Kingdom",
    "latitude": "51.517",
    "longitude": "-0.106"
  },
  "current": {
    "temperature": "15°C",
    "feels_like": "14°C",
    "description": "Partly cloudy",
    "humidity": "76%",
    "wind_speed": "15 km/h",
    "wind_direction": "SW",
    "pressure": "1015 mb",
    "visibility": "10 km",
    "uv_index": "3",
    "cloud_cover": "50%",
    "observation_time": "09:00 AM"
  }
}
```

---

### 2. get_forecast
Get weather forecast for up to 3 days.

**Parameters:**
- `location` (required): City name or location
- `days` (default: 3): Number of forecast days (1-3)
- `units` (default: 'metric'): Temperature units

**Returns:**
- Location information
- Daily forecasts with:
  - Date
  - Max/min/average temperatures
  - Sunrise and sunset times
  - Moon phase
  - Snow accumulation
  - UV index
  - Hourly forecasts (every 3 hours)
    - Time, temperature, feels like
    - Weather description
    - Chance of rain/snow

**Example Usage:**
```json
{
  "method": "get_forecast",
  "arguments": {
    "location": "New York",
    "days": 3,
    "units": "imperial"
  }
}
```

**Example Response:**
```json
{
  "location": {
    "name": "New York",
    "country": "United States of America"
  },
  "forecast": [
    {
      "date": "2025-10-19",
      "max_temp": "72°F",
      "min_temp": "58°F",
      "avg_temp": "65°F",
      "sunrise": "07:03 AM",
      "sunset": "06:18 PM",
      "moon_phase": "Waxing Crescent",
      "total_snow": "0 cm",
      "uv_index": "5",
      "hourly": [
        {
          "time": "0",
          "temp": "60°F",
          "feels_like": "58°F",
          "description": "Clear",
          "chance_of_rain": "0%",
          "chance_of_snow": "0%"
        }
      ]
    }
  ],
  "days": 3
}
```

---

### 3. get_weather_by_coordinates
Get weather using GPS coordinates.

**Parameters:**
- `latitude` (required): Latitude coordinate (-90 to 90)
- `longitude` (required): Longitude coordinate (-180 to 180)
- `units` (default: 'metric'): Temperature units

**Returns:**
- Same as `get_current_weather`

**Example Usage:**
```json
{
  "method": "get_weather_by_coordinates",
  "arguments": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "units": "metric"
  }
}
```

---

### 4. get_moon_phase
Get moon phase and astronomical information.

**Parameters:**
- `location` (optional, default: 'London'): City name or location

**Returns:**
- Location
- Date
- Moon phase (e.g., "New Moon", "Waxing Crescent", "Full Moon")
- Moon illumination percentage
- Moonrise and moonset times
- Sunrise and sunset times

**Example Usage:**
```json
{
  "method": "get_moon_phase",
  "arguments": {
    "location": "Tokyo"
  }
}
```

**Example Response:**
```json
{
  "location": "Tokyo",
  "date": "2025-10-19",
  "moon_phase": "Waxing Crescent",
  "moon_illumination": "35%",
  "moonrise": "11:23 AM",
  "moonset": "10:45 PM",
  "sunrise": "05:53 AM",
  "sunset": "05:18 PM"
}
```

---

## Use Cases

### 1. Travel Planning
Get weather forecasts for travel destinations:
```json
{
  "method": "get_forecast",
  "arguments": {
    "location": "Barcelona",
    "days": 3
  }
}
```

### 2. Real-Time Weather
Check current conditions before going out:
```json
{
  "method": "get_current_weather",
  "arguments": {
    "location": "San Francisco"
  }
}
```

### 3. Coordinate-Based Weather
Get weather for specific GPS locations:
```json
{
  "method": "get_weather_by_coordinates",
  "arguments": {
    "latitude": 51.5074,
    "longitude": -0.1278
  }
}
```

### 4. Astronomy Enthusiasts
Check moon phases for stargazing:
```json
{
  "method": "get_moon_phase",
  "arguments": {
    "location": "Hawaii"
  }
}
```

---

## Location Formats

The tool accepts various location formats:

### City Names
- `"London"`
- `"New York"`
- `"Los Angeles"`

### City, Country
- `"Paris, France"`
- `"Tokyo, Japan"`

### Coordinates
- `"40.7128,-74.0060"` (latitude,longitude)

### Airports
- `"JFK"` (airport codes)
- `"LHR"`

### Special Locations
- `"~Eiffel Tower"` (landmarks)
- `"@stackoverflow.com"` (domain locations)

---

## Temperature Units

### Metric (Default)
- Temperature: Celsius (°C)
- Wind speed: km/h
- Visibility: km
- Precipitation: mm

### Imperial
- Temperature: Fahrenheit (°F)
- Wind speed: mph
- Visibility: miles
- Precipitation: inches

---

## Moon Phases

The tool returns these moon phases:
- **New Moon**: 0-5% illumination
- **Waxing Crescent**: 6-45% illumination, growing
- **First Quarter**: 45-55% illumination
- **Waxing Gibbous**: 56-95% illumination, growing
- **Full Moon**: 96-100% illumination
- **Waning Gibbous**: 95-56% illumination, shrinking
- **Last Quarter**: 55-45% illumination
- **Waning Crescent**: 44-5% illumination, shrinking

---

## Error Handling

### Invalid Location
```json
{
  "error": "Failed to fetch weather data: 404"
}
```

### Missing Required Parameters
```json
{
  "error": "Location is required"
}
```

### Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "status": 429
}
```

---

## Limitations

1. **Forecast Days**: Maximum 3 days forecast
2. **Historical Data**: Not available (current and future only)
3. **Update Frequency**: Data updates every 15-30 minutes
4. **Rate Limiting**: 1000 requests per 10 seconds (configurable)
5. **Hourly Data**: Available in 3-hour intervals

---

## Tips

1. **Use Specific Locations**: "New York, NY" is better than just "New York"
2. **Check Multiple Days**: Use `days: 3` for better planning
3. **Combine Methods**: Get current weather + forecast for complete picture
4. **Coordinates for Precision**: Use lat/long for exact locations
5. **Unit Consistency**: Choose units based on your region

---

## Example Workflows

### Complete Weather Report
```python
# Step 1: Get current weather
current = call_tool("weather_tool", "get_current_weather", {
    "location": "London",
    "units": "metric"
})

# Step 2: Get forecast
forecast = call_tool("weather_tool", "get_forecast", {
    "location": "London",
    "days": 3,
    "units": "metric"
})

# Step 3: Get moon phase
moon = call_tool("weather_tool", "get_moon_phase", {
    "location": "London"
})
```

### Multi-City Comparison
```python
cities = ["London", "New York", "Tokyo", "Sydney"]
for city in cities:
    weather = call_tool("weather_tool", "get_current_weather", {
        "location": city,
        "units": "metric"
    })
    print(f"{city}: {weather['current']['temperature']}")
```

---

## Data Source

- **Provider**: wttr.in
- **Coverage**: Global
- **No API Key**: Free to use
- **Website**: https://wttr.in

---

## Support

For issues or questions:
- Check location spelling
- Try alternative location formats
- Verify internet connectivity
- Check server logs for detailed errors

Happy weather checking! 🌤️

