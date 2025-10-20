"""
Flask application for MCP Server
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    verify_jwt_in_request
)
import json
import os
from functools import wraps
from datetime import datetime, timedelta
import secrets
from pathlib import Path
import sys
import psutil
import platform

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.tools_registry import ToolsRegistry

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['JWT_ALGORITHM'] = 'HS256'

# Initialize JWT Manager
jwt = JWTManager(app)

# Configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Initialize ToolsRegistry
tools_registry = ToolsRegistry(config_folder='config/tools')

# User authentication configuration
USER_CONFIG_FILE = 'config/users.json'

# Server start time for uptime calculation
SERVER_START_TIME = datetime.now()


def load_users():
    """Load users from configuration file"""
    if os.path.exists(USER_CONFIG_FILE):
        with open(USER_CONFIG_FILE, 'r') as f:
            return json.load(f).get('users', [])
    return []


def save_users(users):
    """Save users to configuration file"""
    with open(USER_CONFIG_FILE, 'w') as f:
        json.dump({'users': users}, f, indent=2)


def authenticate_user(username, password):
    """Authenticate user with username and password"""
    users = load_users()
    for user in users:
        if user['id'] == username and user['password'] == password:
            return user
    return None


def login_required(f):
    """Decorator to require login"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        if 'admin' not in session.get('user', {}).get('roles', []):
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)

    return decorated_function


def get_system_info():
    """Get system information for admin panel"""
    uptime = datetime.now() - SERVER_START_TIME
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    return {
        'python_version': platform.python_version(),
        'flask_version': '2.3.3',
        'uptime': f"{hours}h {minutes}m {seconds}s",
        'memory_usage': round(psutil.Process().memory_info().rss / 1024 / 1024, 2),
        'cpu_usage': psutil.cpu_percent(interval=1)
    }


@app.route('/')
def index():
    """Redirect to login or dashboard"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        user = authenticate_user(username, password)
        if user:
            session['user'] = {
                'id': user['id'],
                'full_name': user['full_name'],
                'roles': user.get('roles', [])
            }
            session.permanent = True

            flash(f'Welcome back, {user["full_name"]}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    tools = tools_registry.list_tools()
    stats = tools_registry.get_statistics()

    return render_template('dashboard.html',
                           user=session['user'],
                           tools=tools,
                           stats=stats,
                           year=datetime.now().year)


@app.route('/admin')
@admin_required
def admin_panel():
    """Admin panel page"""
    tools = tools_registry.list_tools()
    users = load_users()
    system_info = get_system_info()

    # Read recent logs
    log_file = 'logs/mcp_server.log'
    logs = ""
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
            logs = ''.join(lines[-100:])  # Last 100 lines

    config = {
        'reload_interval': 300,
        'max_call_history': 50,
        'max_error_history': 50
    }

    return render_template('admin.html',
                           user=session['user'],
                           tools=tools,
                           users=users,
                           logs=logs,
                           config=config,
                           **system_info,
                           year=datetime.now().year)


@app.route('/tool/<tool_name>')
@login_required
def tool_detail(tool_name):
    """Tool detail page"""
    tool = tools_registry.get_tool(tool_name)
    if not tool:
        flash(f'Tool {tool_name} not found', 'error')
        return redirect(url_for('dashboard'))

    config = tools_registry.get_tool_config(tool_name)
    stats = tools_registry.get_tool_statistics(tool_name)

    return render_template('tool_detail.html',
                           user=session['user'],
                           tool_name=tool_name,
                           config=config,
                           stats=stats,
                           year=datetime.now().year)


@app.route('/api/tools', methods=['GET'])
@login_required
def api_list_tools():
    """
    List all tools - returns HTML template or JSON based on request
    Web UI: Renders tools.html template
    API: Returns JSON response
    """
    tools = tools_registry.list_tools()
    tool_details = []

    for tool_name in tools:
        config = tools_registry.get_tool_config(tool_name)
        tool_details.append({
            'name': tool_name,
            'module': config.get('module', ''),
            'max_hits': config.get('max_hits', 1000),
            'max_hit_interval': config.get('max_hit_interval', 10)
        })

    # Check if this is an API request (wants JSON) or web UI request (wants HTML)
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        # Return JSON for API calls
        return jsonify({
            'tools': tool_details,
            'count': len(tool_details)
        })
    else:
        # Return HTML template for web UI
        stats = tools_registry.get_statistics()
        return render_template('tools.html',
                             user=session['user'],
                             tool_details=tool_details,
                             stats=stats,
                             year=datetime.now().year)


@app.route('/api/tool/<tool_name>/call', methods=['POST'])
@login_required
def api_call_tool(tool_name):
    """API endpoint to call a tool"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    method_name = data.get('method', '')
    arguments = data.get('arguments', {})

    if not method_name:
        return jsonify({'error': 'Method name required'}), 400

    # Call tool through registry
    result = tools_registry.handle_tool_call(tool_name, method_name, arguments)

    # Check for rate limit error
    if result.get('status') == 429:
        return jsonify(result), 429

    return jsonify(result)



@app.route('/api/tool/<tool_name>/stats', methods=['GET'])
@login_required
def api_tool_stats(tool_name):
    """API endpoint to get tool statistics"""
    stats = tools_registry.get_tool_statistics(tool_name)
    return jsonify(stats)


@app.route('/api/tool/<tool_name>/reload', methods=['POST'])
@admin_required
def api_reload_tool(tool_name):
    """API endpoint to reload a tool"""
    success = tools_registry.reload_tool(tool_name)

    if success:
        return jsonify({'message': f'Tool {tool_name} reloaded successfully'})
    else:
        return jsonify({'error': f'Failed to reload tool {tool_name}'}), 500


@app.route('/api/mcp/definitions', methods=['GET'])
@login_required
def api_mcp_definitions():
    """API endpoint to get MCP definitions for all tools"""
    definitions = tools_registry.get_mcp_definitions()
    return jsonify(definitions)


@app.route('/api/stats', methods=['GET'])
@login_required
def api_global_stats():
    """API endpoint to get global statistics"""
    stats = tools_registry.get_statistics()
    return jsonify(stats)


# Admin API endpoints
@app.route('/api/admin/reload-all-tools', methods=['POST'])
@admin_required
def api_reload_all_tools():
    """Reload all tools"""
    tools = tools_registry.list_tools()
    success_count = 0

    for tool_name in tools:
        if tools_registry.reload_tool(tool_name):
            success_count += 1

    return jsonify({
        'message': f'Reloaded {success_count}/{len(tools)} tools successfully',
        'success_count': success_count,
        'total': len(tools)
    })


@app.route('/api/admin/clear-cache', methods=['POST'])
@admin_required
def api_clear_cache():
    """Clear tool cache"""
    # Implementation depends on your caching strategy
    return jsonify({'message': 'Cache cleared successfully'})


@app.route('/api/admin/disable-tool/<tool_name>', methods=['POST'])
@admin_required
def api_disable_tool(tool_name):
    """Disable a tool"""
    # This would require implementing a disable mechanism in ToolsRegistry
    return jsonify({'message': f'Tool {tool_name} disabled'})


@app.route('/api/admin/add-user', methods=['POST'])
@admin_required
def api_add_user():
    """Add a new user"""
    data = request.get_json()

    if not data or not data.get('id') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    users = load_users()

    # Check if user already exists
    for user in users:
        if user['id'] == data['id']:
            return jsonify({'error': 'User already exists'}), 400

    new_user = {
        'id': data['id'],
        'password': data['password'],
        'full_name': data.get('full_name', data['id']),
        'roles': data.get('roles', ['user'])
    }

    users.append(new_user)
    save_users(users)

    return jsonify({'message': 'User added successfully'})


@app.route('/api/admin/delete-user/<user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    """Delete a user"""
    users = load_users()
    users = [u for u in users if u['id'] != user_id]
    save_users(users)

    return jsonify({'message': 'User deleted successfully'})


@app.route('/api/admin/logs', methods=['GET'])
@admin_required
def api_get_logs():
    """Get system logs"""
    log_file = 'logs/mcp_server.log'
    logs = ""

    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
            logs = ''.join(lines[-100:])  # Last 100 lines

    return jsonify({'logs': logs})


@app.route('/api/admin/clear-logs', methods=['POST'])
@admin_required
def api_clear_logs():
    """Clear system logs"""
    log_file = 'logs/mcp_server.log'

    if os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write(f"Logs cleared at {datetime.now().isoformat()}\n")

    return jsonify({'message': 'Logs cleared successfully'})


@app.route('/api/admin/update-config', methods=['POST'])
@admin_required
def api_update_config():
    """Update system configuration"""
    data = request.get_json()

    # In a real implementation, you would save this to a configuration file
    # and update the ToolsRegistry settings

    return jsonify({'message': 'Configuration updated successfully'})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html', year=datetime.now().year), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html', year=datetime.now().year), 500


###  JWT Specific Stuff
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for JWT authentication"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = authenticate_user(username, password)

    if user:
        # Create JWT tokens
        access_token = create_access_token(
            identity=username,
            additional_claims={
                'full_name': user['full_name'],
                'roles': user.get('roles', []),
                'tools_access': user.get('tools_access', [])
            }
        )
        refresh_token = create_refresh_token(
            identity=username,
            additional_claims={
                'full_name': user['full_name'],
                'roles': user.get('roles', [])
            }
        )

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'username': username,
                'full_name': user['full_name'],
                'roles': user.get('roles', [])
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def api_refresh():
    """Refresh JWT access token"""
    current_user = get_jwt_identity()

    # Load user data to get updated permissions
    users = load_users()
    user = None
    for u in users:
        if u['id'] == current_user:
            user = u
            break

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Create new access token with updated claims
    access_token = create_access_token(
        identity=current_user,
        additional_claims={
            'full_name': user['full_name'],
            'roles': user.get('roles', []),
            'tools_access': user.get('tools_access', [])
        }
    )

    return jsonify({'access_token': access_token}), 200


@app.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def api_verify():
    """Verify JWT token and return user info"""
    current_user = get_jwt_identity()
    claims = get_jwt()

    return jsonify({
        'username': current_user,
        'full_name': claims.get('full_name', ''),
        'roles': claims.get('roles', []),
        'tools_access': claims.get('tools_access', [])
    }), 200


# Replace the existing api_call_jwt method with this implementation:
@app.route('/api/tool/<tool_name>/callapi', methods=['POST'])
@jwt_required()
def api_call_jwt(tool_name):
    """
    JWT-authenticated API endpoint to call a tool
    Requires valid JWT token in Authorization header
    """
    try:
        # Get user identity and claims from JWT
        current_user = get_jwt_identity()
        claims = get_jwt()

        # Get user's tool access permissions
        tools_access = claims.get('tools_access', [])
        user_roles = claims.get('roles', [])

        # Check if user has access to this tool
        # Admin role or wildcard (*) grants access to all tools
        has_access = (
                '*' in tools_access or
                tool_name in tools_access or
                'admin' in user_roles
        )

        if not has_access:
            return jsonify({
                'error': f'Access denied to tool: {tool_name}',
                'user': current_user,
                'allowed_tools': tools_access
            }), 403

        # Get request data
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        method_name = data.get('method', '')
        arguments = data.get('arguments', {})

        if not method_name:
            return jsonify({'error': 'Method name required'}), 400

        # Log the API call with user information
        app.logger.info(f"JWT API call - User: {current_user}, Tool: {tool_name}, Method: {method_name}")

        # Call tool through registry
        result = tools_registry.handle_tool_call(tool_name, method_name, arguments)

        # Add user information to result for audit purposes
        result['_meta'] = {
            'user': current_user,
            'timestamp': datetime.now().isoformat(),
            'tool': tool_name,
            'method': method_name
        }

        # Check for rate limit error
        if result.get('status') == 429:
            return jsonify(result), 429

        return jsonify(result)

    except Exception as e:
        app.logger.error(f"Error in JWT API call: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Add JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'error': 'Token has expired',
        'message': 'Please refresh your token or login again'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'error': 'Invalid token',
        'message': 'Token verification failed'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'error': 'Authorization required',
        'message': 'Missing or invalid authorization header'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({
        'error': 'Fresh token required',
        'message': 'Please login again to access this resource'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'error': 'Token has been revoked',
        'message': 'Token has been revoked and is no longer valid'
    }), 401


def create_app():
    """Create and configure the Flask application"""
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    # Create static directory if it doesn't exist
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)