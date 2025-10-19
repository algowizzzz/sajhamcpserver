"""
JWT API Usage Examples
Examples of how to use the JWT-authenticated API endpoints
"""

import requests
import json

# Base URL of your MCP server
BASE_URL = "http://localhost:5000"


# 1. Login and get JWT tokens
def login(username, password):
    """Login and get JWT tokens"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": username,
            "password": password
        }
    )

    if response.status_code == 200:
        data = response.json()
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "user": data["user"]
        }
    else:
        print(f"Login failed: {response.json()}")
        return None


# 2. Call a tool with JWT authentication
def call_tool_with_jwt(access_token, tool_name, method, arguments={}):
    """Call a tool using JWT authentication"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{BASE_URL}/api/tool/{tool_name}/callapi",
        headers=headers,
        json={
            "method": method,
            "arguments": arguments
        }
    )

    return response.status_code, response.json()


# 3. Refresh access token
def refresh_token(refresh_token):
    """Refresh the access token"""
    headers = {
        "Authorization": f"Bearer {refresh_token}"
    }

    response = requests.post(
        f"{BASE_URL}/api/auth/refresh",
        headers=headers
    )

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Token refresh failed: {response.json()}")
        return None


# 4. Verify token and get user info
def verify_token(access_token):
    """Verify JWT token and get user information"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        f"{BASE_URL}/api/auth/verify",
        headers=headers
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Token verification failed: {response.json()}")
        return None


# Example usage
if __name__ == "__main__":
    # Login as regular user
    print("=== Login as user1 ===")
    auth = login("user1", "user123")

    if auth:
        print(f"Logged in as: {auth['user']['full_name']}")
        access_token = auth['access_token']

        # Verify token and check permissions
        print("\n=== Verify Token ===")
        user_info = verify_token(access_token)
        if user_info:
            print(f"User: {user_info['username']}")
            print(f"Roles: {user_info['roles']}")
            print(f"Tools access: {user_info['tools_access']}")

        # Try to call an allowed tool (wikipedia)
        print("\n=== Call Wikipedia Tool (Allowed) ===")
        status, result = call_tool_with_jwt(
            access_token,
            "wikipedia",
            "search_articles",
            {"query": "Python programming", "limit": 5}
        )
        print(f"Status: {status}")
        print(f"Result: {json.dumps(result, indent=2)[:500]}...")

        # Try to call a restricted tool (fed_reserve - not in user1's access list)
        print("\n=== Call Fed Reserve Tool (Restricted) ===")
        status, result = call_tool_with_jwt(
            access_token,
            "fed_reserve",
            "get_interest_rates",
            {"rate_type": "federal_funds"}
        )
        print(f"Status: {status}")
        print(f"Result: {json.dumps(result, indent=2)}")

    # Login as admin
    print("\n\n=== Login as admin ===")
    admin_auth = login("admin", "admin123")

    if admin_auth:
        print(f"Logged in as: {admin_auth['user']['full_name']}")
        admin_token = admin_auth['access_token']

        # Admin can access any tool
        print("\n=== Admin calls Fed Reserve Tool ===")
        status, result = call_tool_with_jwt(
            admin_token,
            "fed_reserve",
            "get_interest_rates",
            {"rate_type": "federal_funds"}
        )
        print(f"Status: {status}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")

# Example using curl commands
"""
# 1. Login and get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "user123"}'

# 2. Call tool with JWT token (replace YOUR_TOKEN with actual token)
curl -X POST http://localhost:5000/api/tool/wikipedia/callapi \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"method": "search_articles", "arguments": {"query": "Python"}}'

# 3. Refresh token
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"

# 4. Verify token
curl -X GET http://localhost:5000/api/auth/verify \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
"""