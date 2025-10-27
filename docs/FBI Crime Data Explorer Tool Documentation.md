# FBI Crime Data Explorer Tool Documentation

```
Copyright All rights Reserved 2025-2030, Ashutosh Sinha
Email: ajsinha@gmail.com
```

## Overview

The FBI Crime Data Explorer Tool provides programmatic access to crime statistics and data from the Federal Bureau of Investigation's Crime Data Explorer API. This tool enables retrieval of national, state, and agency-level crime statistics including violent crimes, property crimes, and various offense types.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Actions](#actions)
- [Usage Examples](#usage-examples)
  - [API Call Examples](#api-call-examples)
  - [Web UI Examples](#web-ui-examples)
- [Data Sources](#data-sources)
- [Limitations](#limitations)
- [Support](#support)

## Features

- **National Statistics**: Retrieve nationwide crime statistics
- **State Statistics**: Get crime data for specific US states
- **Agency Statistics**: Access crime data from individual law enforcement agencies
- **Agency Search**: Search for law enforcement agencies by name or state
- **Offense Data**: Get detailed offense-specific data
- **Crime Trends**: Analyze crime trends over multiple years
- **State Comparisons**: Compare crime statistics across multiple states
- **Participation Rates**: View UCR reporting participation rates
- **No API Key Required**: Public data access without authentication

## Installation

### Prerequisites

```bash
Python 3.8 or higher
```

### Required Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### File Structure

```
project/
├── tools/
│   └── impl/
│       └── fbi_tool.py          # Main tool implementation
├── config/
│   └── fbi.json                 # Tool configuration
└── clients/
    └── fbi_client.py            # Standalone client
```

## Configuration

### JSON Configuration (fbi.json)

The tool is configured through a JSON file that defines the tool's metadata, input schema, and capabilities:

```json
{
  "name": "fbi",
  "implementation": "tools.impl.fbi_tool.FBITool",
  "description": "Retrieve US crime statistics and data from FBI Crime Data Explorer",
  "version": "1.0.0",
  "enabled": true,
  "metadata": {
    "author": "Ashutosh Sinha",
    "category": "Crime Statistics",
    "tags": ["crime", "fbi", "statistics", "law enforcement", "usa", "ucr"],
    "rateLimit": 120,
    "cacheTTL": 3600
  }
}
```

## Actions

The FBI tool supports the following actions:

### 1. get_national_statistics

Retrieve national-level crime statistics for a specific year and offense type.

**Parameters:**
- `year` (integer, optional): Year for statistics (defaults to latest available)
- `offense_type` (string, optional): Type of crime (defaults to 'violent_crime')
- `per_capita` (boolean, optional): Return per capita statistics (defaults to false)

**Offense Types:**
- `violent_crime` - All violent crimes
- `homicide` - Murder and non-negligent manslaughter
- `rape` - Rape (revised definition)
- `robbery` - Robbery
- `aggravated_assault` - Aggravated assault
- `property_crime` - All property crimes
- `burglary` - Burglary
- `larceny` - Larceny-theft
- `motor_vehicle_theft` - Motor vehicle theft
- `arson` - Arson

### 2. get_state_statistics

Retrieve crime statistics for a specific US state.

**Parameters:**
- `state` (string, **required**): US state abbreviation (e.g., 'CA', 'NY', 'TX')
- `year` (integer, optional): Year for statistics
- `offense_type` (string, optional): Type of crime
- `per_capita` (boolean, optional): Return per capita statistics

### 3. get_agency_statistics

Get crime statistics for a specific law enforcement agency.

**Parameters:**
- `ori` (string, **required**): Originating Agency Identifier (ORI) code
- `year` (integer, optional): Year for statistics
- `offense_type` (string, optional): Type of crime

### 4. search_agencies

Search for law enforcement agencies by name or state.

**Parameters:**
- `state` (string, optional): Filter by US state abbreviation
- `agency_name` (string, optional): Filter by agency name

### 5. get_offense_data

Get detailed data for all offense types.

**Parameters:**
- `year` (integer, optional): Year for statistics
- `state` (string, optional): Filter by US state

### 6. get_participation_rate

Get UCR (Uniform Crime Reporting) program participation rates.

**Parameters:**
- `year` (integer, optional): Year for statistics
- `state` (string, optional): Filter by US state

### 7. get_agency_details

Get detailed information about a specific law enforcement agency.

**Parameters:**
- `ori` (string, **required**): Originating Agency Identifier (ORI) code

### 8. get_crime_trend

Analyze crime trends over multiple years.

**Parameters:**
- `state` (string, optional): Filter by US state (omit for national trends)
- `offense_type` (string, optional): Type of crime
- `start_year` (integer, optional): Start year for trend analysis
- `end_year` (integer, optional): End year for trend analysis
- `per_capita` (boolean, optional): Return per capita statistics

### 9. compare_states

Compare crime statistics across multiple states.

**Parameters:**
- `states` (array, **required**): List of state abbreviations (minimum 2)
- `year` (integer, optional): Year for comparison
- `offense_type` (string, optional): Type of crime
- `per_capita` (boolean, optional): Return per capita statistics

## Usage Examples

### API Call Examples

#### Example 1: Get National Violent Crime Statistics

```python
import requests
import json

# API endpoint
url = "http://localhost:5000/api/tools/execute"

# Request payload
payload = {
    "tool_name": "fbi",
    "arguments": {
        "action": "get_national_statistics",
        "year": 2022,
        "offense_type": "violent_crime",
        "per_capita": True
    }
}

# Make request
response = requests.post(url, json=payload)
result = response.json()

print(json.dumps(result, indent=2))
```

**Sample Response:**
```json
{
  "year": 2022,
  "offense_type": "violent_crime",
  "offense_category": "violent-crime",
  "per_capita": true,
  "data": {
    "actual": 380473,
    "cleared": 201453,
    "rate": 1145.3
  },
  "source": "FBI Crime Data Explorer",
  "retrieved_at": "2025-10-26T10:30:00"
}
```

#### Example 2: Get California Crime Statistics

```python
payload = {
    "tool_name": "fbi",
    "arguments": {
        "action": "get_state_statistics",
        "state": "CA",
        "year": 2022,
        "offense_type": "homicide",
        "per_capita": True
    }
}

response = requests.post(url, json=payload)
result = response.json()
```

**Sample Response:**
```json
{
  "state": "CA",
  "state_name": "California",
  "year": 2022,
  "offense_type": "homicide",
  "offense_category": "homicide",
  "per_capita": true,
  "data": {
    "actual": 2197,
    "cleared": 1423,
    "rate": 5.6
  },
  "source": "FBI Crime Data Explorer"
}
```

#### Example 3: Search for Agencies in New York

```python
payload = {
    "tool_name": "fbi",
    "arguments": {
        "action": "search_agencies",
        "state": "NY",
        "agency_name": "Police"
    }
}

response = requests.post(url, json=payload)
result = response.json()
```

**Sample Response:**
```json
{
  "search_criteria": {
    "state": "NY",
    "agency_name": "Police"
  },
  "agencies": [
    {
      "ori": "NY03000",
      "agency_name": "New York City Police Department",
      "state": "NY",
      "city": "New York",
      "population": 8336817
    },
    {
      "ori": "NY00102",
      "agency_name": "Albany Police Department",
      "state": "NY",
      "city": "Albany",
      "population": 97478
    }
  ],
  "total_count": 2
}
```

#### Example 4: Get Crime Trend Analysis

```python
payload = {
    "tool_name": "fbi",
    "arguments": {
        "action": "get_crime_trend",
        "state": "TX",
        "offense_type": "violent_crime",
        "start_year": 2018,
        "end_year": 2022,
        "per_capita": True
    }
}

response = requests.post(url, json=payload)
result = response.json()
```

**Sample Response:**
```json
{
  "state": "TX",
  "state_name": "Texas",
  "offense_type": "violent_crime",
  "start_year": 2018,
  "end_year": 2022,
  "per_capita": true,
  "trend": [
    {"year": 2018, "data": {"actual": 115552, "rate": 410.9}},
    {"year": 2019, "data": {"actual": 119180, "rate": 419.4}},
    {"year": 2020, "data": {"actual": 128736, "rate": 445.9}},
    {"year": 2021, "data": {"actual": 135246, "rate": 463.8}},
    {"year": 2022, "data": {"actual": 131084, "rate": 443.5}}
  ]
}
```

#### Example 5: Compare Multiple States

```python
payload = {
    "tool_name": "fbi",
    "arguments": {
        "action": "compare_states",
        "states": ["CA", "TX", "FL", "NY"],
        "year": 2022,
        "offense_type": "violent_crime",
        "per_capita": True
    }
}

response = requests.post(url, json=payload)
result = response.json()
```

**Sample Response:**
```json
{
  "year": 2022,
  "offense_type": "violent_crime",
  "per_capita": true,
  "states": {
    "CA": {
      "state_name": "California",
      "data": {"actual": 177627, "rate": 452.0}
    },
    "TX": {
      "state_name": "Texas",
      "data": {"actual": 131084, "rate": 443.5}
    },
    "FL": {
      "state_name": "Florida",
      "data": {"actual": 84468, "rate": 380.9}
    },
    "NY": {
      "state_name": "New York",
      "data": {"actual": 75923, "rate": 388.2}
    }
  }
}
```

#### Example 6: Get Agency Details

```python
payload = {
    "tool_name": "fbi",
    "arguments": {
        "action": "get_agency_details",
        "ori": "CA01942"
    }
}

response = requests.post(url, json=payload)
result = response.json()
```

#### Example 7: Get Offense Data for a State

```python
payload = {
    "tool_name": "fbi",
    "arguments": {
        "action": "get_offense_data",
        "year": 2022,
        "state": "FL"
    }
}

response = requests.post(url, json=payload)
result = response.json()
```

#### Example 8: Get Participation Rate

```python
payload = {
    "tool_name": "fbi",
    "arguments": {
        "action": "get_participation_rate",
        "year": 2022,
        "state": "CA"
    }
}

response = requests.post(url, json=payload)
result = response.json()
```

### Web UI Examples

The FBI tool can also be accessed through a web-based user interface. Below are examples of how to use the tool through the web UI.

#### Example 1: Get National Statistics via Web UI

1. Navigate to the MCP Server Web UI at `http://localhost:5000`
2. Select the **FBI** tool from the tools dropdown
3. Fill in the form:
   - **Action**: `get_national_statistics`
   - **Year**: `2022`
   - **Offense Type**: `violent_crime`
   - **Per Capita**: `true`
4. Click **Execute Tool**
5. View the results in the response panel

#### Example 2: Search for Agencies via Web UI

1. Navigate to the MCP Server Web UI
2. Select the **FBI** tool
3. Fill in the form:
   - **Action**: `search_agencies`
   - **State**: `NY`
   - **Agency Name**: `Police`
4. Click **Execute Tool**
5. Browse the list of matching agencies

#### Example 3: Compare States via Web UI

1. Navigate to the MCP Server Web UI
2. Select the **FBI** tool
3. Fill in the form:
   - **Action**: `compare_states`
   - **States**: `["CA", "TX", "FL", "NY"]`
   - **Year**: `2022`
   - **Offense Type**: `violent_crime`
   - **Per Capita**: `true`
4. Click **Execute Tool**
5. View the comparative statistics

#### Example 4: Get Crime Trend via Web UI

1. Navigate to the MCP Server Web UI
2. Select the **FBI** tool
3. Fill in the form:
   - **Action**: `get_crime_trend`
   - **State**: `TX`
   - **Offense Type**: `robbery`
   - **Start Year**: `2018`
   - **End Year**: `2022`
   - **Per Capita**: `true`
4. Click **Execute Tool**
5. Analyze the trend data displayed

## Data Sources

The FBI tool retrieves data from the following sources:

- **FBI Crime Data Explorer API**: https://api.usa.gov/crime/fbi/cde
- **UCR Program**: Uniform Crime Reporting (UCR) Program data
- **NIBRS**: National Incident-Based Reporting System (where available)

### Data Coverage

- **Timeframe**: Data typically available from 1960 to present (with a 1-2 year lag)
- **Geography**: All 50 US states, District of Columbia, and US territories
- **Agencies**: Over 18,000 law enforcement agencies
- **Offense Types**: 10 major offense categories

## US State Abbreviations

The tool accepts the following US state abbreviations:

| Abbreviation | State Name |
|-------------|------------|
| AL | Alabama |
| AK | Alaska |
| AZ | Arizona |
| AR | Arkansas |
| CA | California |
| CO | Colorado |
| CT | Connecticut |
| DE | Delaware |
| FL | Florida |
| GA | Georgia |
| HI | Hawaii |
| ID | Idaho |
| IL | Illinois |
| IN | Indiana |
| IA | Iowa |
| KS | Kansas |
| KY | Kentucky |
| LA | Louisiana |
| ME | Maine |
| MD | Maryland |
| MA | Massachusetts |
| MI | Michigan |
| MN | Minnesota |
| MS | Mississippi |
| MO | Missouri |
| MT | Montana |
| NE | Nebraska |
| NV | Nevada |
| NH | New Hampshire |
| NJ | New Jersey |
| NM | New Mexico |
| NY | New York |
| NC | North Carolina |
| ND | North Dakota |
| OH | Ohio |
| OK | Oklahoma |
| OR | Oregon |
| PA | Pennsylvania |
| RI | Rhode Island |
| SC | South Carolina |
| SD | South Dakota |
| TN | Tennessee |
| TX | Texas |
| UT | Utah |
| VT | Vermont |
| VA | Virginia |
| WA | Washington |
| WV | West Virginia |
| WI | Wisconsin |
| WY | Wyoming |
| DC | District of Columbia |

## Limitations

### Data Availability

- Crime statistics typically have a 1-2 year lag from the current year
- Not all agencies report data to the FBI
- Some states have incomplete data for certain years
- Participation rates vary by state and year

### API Limitations

- Rate limit: 120 requests per minute
- No API key required for public data
- Cache TTL: 1 hour (3600 seconds)
- Response timeout: 30 seconds

### Data Quality

- Data is self-reported by law enforcement agencies
- Reporting standards and definitions may vary
- Some agencies may not participate in UCR reporting
- Historical data may be revised

## Error Handling

The tool implements comprehensive error handling:

```python
try:
    result = fbi_tool.execute({
        "action": "get_state_statistics",
        "state": "CA",
        "year": 2022
    })
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

Common errors:
- `ValueError`: Invalid parameters (e.g., invalid state code)
- `HTTPError 404`: Resource not found
- `HTTPError 500`: Server error
- `Timeout`: Request timeout exceeded

## Best Practices

1. **Use Per Capita Statistics**: For meaningful comparisons between states or jurisdictions, always use per capita rates
2. **Consider Participation Rates**: Check participation rates before drawing conclusions
3. **Analyze Trends**: Look at multi-year trends rather than single-year data
4. **Cache Results**: Implement caching for frequently accessed data
5. **Handle Missing Data**: Always check for null or missing values in responses
6. **Respect Rate Limits**: Implement exponential backoff for rate limit errors

## Support

For support, issues, or feature requests:

- **Email**: ajsinha@gmail.com
- **Tool Version**: 1.0.0
- **Last Updated**: October 2025

## License

```
Copyright All rights Reserved 2025-2030, Ashutosh Sinha
Email: ajsinha@gmail.com
```

## Changelog

### Version 1.0.0 (October 2025)
- Initial release
- Support for 9 actions
- National, state, and agency-level statistics
- Crime trend analysis
- State comparison capabilities
- Agency search functionality
- No API key required

## Additional Resources

- FBI Crime Data Explorer: https://crime-data-explorer.fr.cloud.gov/
- UCR Program: https://www.fbi.gov/services/cjis/ucr
- API Documentation: https://crime-data-explorer.fr.cloud.gov/pages/docApi
- NIBRS User Manual: https://www.fbi.gov/services/cjis/ucr/nibrs-user-manual

## Appendix A: Complete Action Reference

### Action Matrix

| Action | Required Parameters | Optional Parameters | Returns |
|--------|-------------------|-------------------|---------|
| get_national_statistics | - | year, offense_type, per_capita | National crime statistics |
| get_state_statistics | state | year, offense_type, per_capita | State crime statistics |
| get_agency_statistics | ori | year, offense_type | Agency crime statistics |
| search_agencies | - | state, agency_name | List of agencies |
| get_offense_data | - | year, state | Detailed offense data |
| get_participation_rate | - | year, state | Participation rates |
| get_agency_details | ori | - | Agency information |
| get_crime_trend | - | state, offense_type, start_year, end_year, per_capita | Trend analysis |
| compare_states | states | year, offense_type, per_capita | State comparison |

## Appendix B: Sample Integration Code

### Flask Integration

```python
from flask import Flask, request, jsonify
from tools.impl.fbi_tool import FBITool

app = Flask(__name__)
fbi_tool = FBITool()

@app.route('/api/fbi/statistics', methods=['POST'])
def get_statistics():
    try:
        data = request.json
        result = fbi_tool.execute(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
```

### Async Integration

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from tools.impl.fbi_tool import FBITool

async def get_multiple_states(states, year):
    fbi_tool = FBITool()
    executor = ThreadPoolExecutor(max_workers=5)
    
    tasks = []
    for state in states:
        task = asyncio.get_event_loop().run_in_executor(
            executor,
            fbi_tool.execute,
            {
                "action": "get_state_statistics",
                "state": state,
                "year": year,
                "offense_type": "violent_crime"
            }
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# Usage
states = ["CA", "TX", "FL", "NY"]
results = asyncio.run(get_multiple_states(states, 2022))
```