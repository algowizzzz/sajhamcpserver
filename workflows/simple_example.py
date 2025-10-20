#!/usr/bin/env python3
"""
Simple Wikipedia Workflow - Minimal Example
============================================

This is the simplest possible workflow example.
Perfect for absolute beginners!

Just searches Wikipedia and prints results.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5002"
USERNAME = "admin"
PASSWORD = "admin123"

# Create a session to maintain login
session = requests.Session()

# Step 1: Login
print("Step 1: Logging in...")
session.post(f"{BASE_URL}/login", data={
    "username": USERNAME,
    "password": PASSWORD
})
print("✅ Logged in!\n")

# Step 2: Search Wikipedia
print("Step 2: Searching Wikipedia for 'Python'...")
response = session.post(
    f"{BASE_URL}/api/tool/wikipedia_tool/call",
    json={
        "method": "search_articles",
        "arguments": {
            "query": "Python",
            "limit": 3
        }
    }
)

result = response.json()
print("✅ Search complete!\n")

# Step 3: Display results
print("Results:")
print(json.dumps(result, indent=2))

print("\n✨ Done!")

