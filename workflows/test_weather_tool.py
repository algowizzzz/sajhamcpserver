#!/usr/bin/env python3
"""
Weather Tool Test Script
Test all methods of the new Weather MCP Tool
"""
import requests
import json

# Setup
base_url = "http://localhost:5002"
session = requests.Session()

# Login
print("🔐 Logging in...")
session.post(f"{base_url}/login", data={"username": "admin", "password": "admin123"})
print("✅ Logged in!\n")

def call_weather_tool(method, arguments):
    """Helper to call weather tool"""
    response = session.post(
        f"{base_url}/api/tool/weather_tool/call",
        json={"method": method, "arguments": arguments}
    )
    return response.json()

# Test 1: Current Weather
print("=" * 60)
print("TEST 1: Current Weather (London)")
print("=" * 60)
result = call_weather_tool("get_current_weather", {
    "location": "London",
    "units": "metric"
})
print(f"Location: {result['location']['name']}, {result['location']['country']}")
print(f"Temperature: {result['current']['temperature']}")
print(f"Feels Like: {result['current']['feels_like']}")
print(f"Description: {result['current']['description']}")
print(f"Wind: {result['current']['wind_speed']} {result['current']['wind_direction']}")
print(f"Humidity: {result['current']['humidity']}")
print()

# Test 2: Forecast
print("=" * 60)
print("TEST 2: 2-Day Forecast (New York)")
print("=" * 60)
result = call_weather_tool("get_forecast", {
    "location": "New York",
    "days": 2,
    "units": "imperial"
})
print(f"Location: {result['location']['name']}")
for i, day in enumerate(result['forecast'], 1):
    print(f"\nDay {i}: {day['date']}")
    print(f"  Max: {day['max_temp']}, Min: {day['min_temp']}")
    print(f"  Sunrise: {day['sunrise']}, Sunset: {day['sunset']}")
print()

# Test 3: Coordinates
print("=" * 60)
print("TEST 3: Weather by Coordinates (Tokyo)")
print("=" * 60)
result = call_weather_tool("get_weather_by_coordinates", {
    "latitude": 35.6762,
    "longitude": 139.6503,
    "units": "metric"
})
print(f"Location: {result['location']['name']}")
print(f"Temperature: {result['current']['temperature']}")
print(f"Description: {result['current']['description']}")
print()

# Test 4: Moon Phase
print("=" * 60)
print("TEST 4: Moon Phase (Paris)")
print("=" * 60)
result = call_weather_tool("get_moon_phase", {
    "location": "Paris"
})
print(f"Date: {result['date']}")
print(f"Moon Phase: {result['moon_phase']}")
print(f"Illumination: {result['moon_illumination']}")
print(f"Moonrise: {result['moonrise']}, Moonset: {result['moonset']}")
print(f"Sunrise: {result['sunrise']}, Sunset: {result['sunset']}")
print()

print("=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
