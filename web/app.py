"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Flask application for SAJHA MCP Server
"""

import json
import logging
import csv
import io
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps

# Import core modules
from core.auth_manager import AuthManager
from core.mcp_handler import MCPHandler
from tools.tools_registry import ToolsRegistry

# Global instances
app = None
socketio = None
auth_manager = None
mcp_handler = None
tools_registry = None

def create_app():
    """Create and configure Flask application"""
    global app, socketio, auth_manager, mcp_handler, tools_registry

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sajha-mcp-server-secret-key-2025'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

    # Enable CORS
    CORS(app)

    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    # Initialize managers
    auth_manager = AuthManager()
    tools_registry = ToolsRegistry()
    mcp_handler = MCPHandler(tools_registry=tools_registry, auth_manager=auth_manager)

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Register routes
    register_routes(app)
    register_socketio_handlers(socketio)

    return app, socketio

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('login', next=request.url))

        # Validate session
        session_data = auth_manager.validate_session(session['token'])
        if not session_data:
            session.pop('token', None)
            return redirect(url_for('login', next=request.url))

        # Store session data in g for use in view
        request.user_session = session_data
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('login'))

        session_data = auth_manager.validate_session(session['token'])
        if not session_data or not auth_manager.is_admin(session_data):
            return render_template('error.html',
                                 error="Access Denied",
                                 message="Admin privileges required"), 403

        request.user_session = session_data
        return f(*args, **kwargs)
    return decorated_function

def register_routes(app):
    """Register Flask routes"""

    @app.route('/')
    def index():
        """Home page"""
        return redirect(url_for('dashboard'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page"""
        if request.method == 'POST':
            user_id = request.form.get('user_id')
            password = request.form.get('password')

            # Authenticate user
            token = auth_manager.authenticate(user_id, password)
            if token:
                session['token'] = token
                session.permanent = True

                # Redirect to next page or dashboard
                next_page = request.args.get('next', url_for('dashboard'))
                return redirect(next_page)
            else:
                return render_template('login.html', error="Invalid credentials")

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        """Logout"""
        token = session.get('token')
        if token:
            auth_manager.logout(token)
        session.pop('token', None)
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard page"""
        user_session = request.user_session

        # Get available tools
        tools = tools_registry.get_all_tools()

        # Filter tools based on user permissions
        if not auth_manager.is_admin(user_session):
            accessible_tools = auth_manager.get_user_accessible_tools(user_session)
            if '*' not in accessible_tools:
                tools = [t for t in tools if t['name'] in accessible_tools]

        # Get tool errors if admin
        tool_errors = []
        if auth_manager.is_admin(user_session):
            tool_errors = tools_registry.get_tool_errors()

        return render_template('dashboard.html',
                             user=user_session,
                             tools=tools,
                             tool_errors=tool_errors,
                             is_admin=auth_manager.is_admin(user_session))

    @app.route('/tools')
    @login_required
    def tools_list():
        """Tools list page"""
        user_session = request.user_session

        # Get all tools
        tools = tools_registry.get_all_tools()

        # Filter based on user permissions
        accessible_tools = auth_manager.get_user_accessible_tools(user_session)
        if '*' not in accessible_tools:
            tools = [t for t in tools if t['name'] in accessible_tools]

        return render_template('tools_list.html',
                             user=user_session,
                             tools=tools)

    @app.route('/tools/execute/<tool_name>')
    @login_required
    def tool_execute(tool_name):
        """Tool execution page"""
        user_session = request.user_session

        # Check if user has access to this tool
        if not auth_manager.has_tool_access(user_session, tool_name):
            return render_template('error.html',
                                 error="Access Denied",
                                 message=f"You don't have permission to use {tool_name}"), 403

        # Get tool details
        tool = tools_registry.get_tool(tool_name)
        if not tool:
            return render_template('error.html',
                                 error="Tool Not Found",
                                 message=f"Tool {tool_name} not found"), 404

        return render_template('tool_execute.html',
                             user=user_session,
                             tool=tool.to_mcp_format())

    @app.route('/admin/tools')
    @admin_required
    def admin_tools():
        """Admin tools management page"""
        user_session = request.user_session

        # Get all tools with metrics
        tools_metrics = tools_registry.get_tool_metrics()
        tool_errors = tools_registry.get_tool_errors()

        return render_template('admin_tools.html',
                             user=user_session,
                             tools_metrics=tools_metrics,
                             tool_errors=tool_errors)

    @app.route('/admin/tools/<tool_name>/config')
    @admin_required
    def tool_config_page(tool_name):
        """Tool configuration editor page"""
        user_session = request.user_session

        # Verify tool exists
        tool = tools_registry.get_tool(tool_name)
        if not tool and tool_name not in tools_registry.tool_configs:
            return render_template('error.html',
                                 user=user_session,
                                 error="Tool Not Found",
                                 message=f"Tool '{tool_name}' does not exist"), 404

        return render_template('tool_config.html',
                             user=user_session,
                             tool_name=tool_name)

    @app.route('/admin/users')
    @admin_required
    def admin_users():
        """Admin users management page"""
        user_session = request.user_session

        # Get all users
        users = auth_manager.get_all_users()

        return render_template('admin_users.html',
                             user=user_session,
                             users=users)

    @app.route('/monitoring/tools')
    @login_required
    def monitoring_tools():
        """Tools monitoring page"""
        user_session = request.user_session

        # Get tool metrics
        metrics = tools_registry.get_tool_metrics()

        return render_template('monitoring_tools.html',
                             user=user_session,
                             metrics=metrics)

    @app.route('/monitoring/users')
    @admin_required
    def monitoring_users():
        """Users monitoring page"""
        user_session = request.user_session

        # Get user activity (simplified for now)
        users = auth_manager.get_all_users()

        return render_template('monitoring_users.html',
                             user=user_session,
                             users=users)

    # API Routes
    @app.route('/api/mcp', methods=['POST'])
    def mcp_endpoint():
        """MCP protocol endpoint for HTTP requests"""
        # Get authorization header
        auth_header = request.headers.get('Authorization', '')

        # Validate token
        session_data = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            session_data = auth_manager.validate_session(token)

        # Get request data
        try:
            request_data = request.get_json()
        except:
            return jsonify({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }), 400

        # Handle request
        response = mcp_handler.handle_request(request_data, session_data)
        return jsonify(response)

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        """API login endpoint"""
        data = request.get_json()
        user_id = data.get('user_id')
        password = data.get('password')

        if not user_id or not password:
            return jsonify({'error': 'Missing credentials'}), 400

        token = auth_manager.authenticate(user_id, password)
        if token:
            session_data = auth_manager.validate_session(token)
            return jsonify({
                'token': token,
                'user': {
                    'user_id': session_data['user_id'],
                    'user_name': session_data['user_name'],
                    'roles': session_data['roles']
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    @app.route('/api/tools/execute', methods=['POST'])
    def api_tool_execute():
        """API endpoint for tool execution"""
        # Get authorization
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401

        token = auth_header[7:]
        session_data = auth_manager.validate_session(token)
        if not session_data:
            return jsonify({'error': 'Invalid token'}), 401

        # Get request data
        data = request.get_json()
        tool_name = data.get('tool')
        arguments = data.get('arguments', {})

        # Check access
        if not auth_manager.has_tool_access(session_data, tool_name):
            return jsonify({'error': 'Access denied'}), 403

        # Execute tool
        try:
            tool = tools_registry.get_tool(tool_name)
            if not tool:
                return jsonify({'error': 'Tool not found'}), 404

            result = tool.execute_with_tracking(arguments)
            return jsonify({
                'success': True,
                'result': result
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/admin/tools/<tool_name>/enable', methods=['POST'])
    @admin_required
    def api_enable_tool(tool_name):
        """Enable a tool"""
        success = tools_registry.enable_tool(tool_name)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Tool not found'}), 404

    @app.route('/api/admin/tools/<tool_name>/disable', methods=['POST'])
    @admin_required
    def api_disable_tool(tool_name):
        """Disable a tool"""
        success = tools_registry.disable_tool(tool_name)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Tool not found'}), 404

    @app.route('/api/admin/tools/metrics/export')
    @admin_required
    def api_export_metrics():
        """Export tool metrics as CSV"""
        try:
            # Get all tool metrics
            metrics = tools_registry.get_tool_metrics()

            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow([
                'Tool Name',
                'Version',
                'Status',
                'Execution Count',
                'Average Execution Time (s)',
                'Last Execution',
                'Description'
            ])

            # Write data
            for metric in metrics:
                writer.writerow([
                    metric.get('name', ''),
                    metric.get('version', ''),
                    'Enabled' if metric.get('enabled', False) else 'Disabled',
                    metric.get('execution_count', 0),
                    f"{metric.get('average_execution_time', 0):.3f}",
                    metric.get('last_execution', 'Never'),
                    metric.get('description', '')
                ])

            # Prepare response
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=tool_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

            return response

        except Exception as e:
            logging.error(f"Error exporting metrics: {e}")
            return jsonify({'error': 'Failed to export metrics'}), 500

    @app.route('/api/admin/tools/<tool_name>/config', methods=['GET'])
    @admin_required
    def api_get_tool_config(tool_name):
        """Get tool configuration"""
        try:
            # First try to get from tool_configs
            if tool_name in tools_registry.tool_configs:
                return jsonify(tools_registry.tool_configs[tool_name])

            # Otherwise get from tool instance
            tool = tools_registry.get_tool(tool_name)
            if tool:
                return jsonify(tool.config)

            return jsonify({'error': 'Tool not found'}), 404

        except Exception as e:
            logging.error(f"Error getting tool config: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/tools/<tool_name>/config', methods=['POST'])
    @admin_required
    def api_save_tool_config(tool_name):
        """Save tool configuration"""
        try:
            config = request.get_json()

            if not config:
                return jsonify({'error': 'No configuration provided'}), 400

            # Validate required fields
            required_fields = ['name', 'description', 'version', 'enabled', 'inputSchema']
            for field in required_fields:
                if field not in config:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Ensure name matches
            if config['name'] != tool_name:
                return jsonify({'error': 'Tool name in configuration does not match'}), 400

            # Update the tool configuration
            tools_registry.tool_configs[tool_name] = config

            # Save to file
            tools_registry._save_tool_config(tool_name)

            # If tool is already loaded, unregister and reload it
            if tool_name in tools_registry.tools:
                tools_registry.unregister_tool(tool_name)

            # Reload the tool with new config
            config_file = Path(tools_registry.tools_config_dir) / f"{tool_name}.json"
            if config_file.exists():
                tools_registry.load_tool_from_config(config_file)

            return jsonify({
                'success': True,
                'message': 'Configuration saved successfully'
            })

        except Exception as e:
            logging.error(f"Error saving tool config: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/tools/<tool_name>/delete', methods=['DELETE'])
    @admin_required
    def api_delete_tool(tool_name):
        """Delete a tool configuration"""
        try:
            # Unregister tool if loaded
            if tool_name in tools_registry.tools:
                tools_registry.unregister_tool(tool_name)

            # Remove from configs
            if tool_name in tools_registry.tool_configs:
                del tools_registry.tool_configs[tool_name]

            # Delete configuration file
            config_file = Path(tools_registry.tools_config_dir) / f"{tool_name}.json"
            if config_file.exists():
                os.remove(config_file)

            return jsonify({
                'success': True,
                'message': f'Tool {tool_name} deleted successfully'
            })

        except Exception as e:
            logging.error(f"Error deleting tool: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/tools/reload', methods=['POST'])
    @admin_required
    def api_reload_tools():
        """Reload all tools from configuration"""
        try:
            tools_registry.reload_all_tools()
            return jsonify({
                'success': True,
                'message': 'Tools reloaded successfully'
            })
        except Exception as e:
            logging.error(f"Error reloading tools: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })

    @app.errorhandler(404)
    def not_found(error):
        """404 error handler"""
        return render_template('error.html',
                             error="Page Not Found",
                             message="The requested page does not exist"), 404

    @app.errorhandler(500)
    def internal_error(error):
        """500 error handler"""
        return render_template('error.html',
                             error="Internal Server Error",
                             message="An unexpected error occurred"), 500

def register_socketio_handlers(socketio):
    """Register SocketIO event handlers"""

    @socketio.on('connect')
    def handle_connect():
        """Handle WebSocket connection"""
        logging.info(f"WebSocket client connected: {request.sid}")
        emit('connected', {'message': 'Connected to SAJHA MCP Server'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle WebSocket disconnection"""
        logging.info(f"WebSocket client disconnected: {request.sid}")

    @socketio.on('authenticate')
    def handle_authenticate(data):
        """Handle WebSocket authentication"""
        token = data.get('token')
        if token:
            session_data = auth_manager.validate_session(token)
            if session_data:
                emit('authenticated', {
                    'success': True,
                    'user': session_data['user_name']
                })
                return

        emit('authenticated', {'success': False, 'error': 'Invalid token'})
        disconnect()

    @socketio.on('mcp_request')
    def handle_mcp_request(data):
        """Handle MCP request over WebSocket"""
        # Validate session
        token = data.get('token')
        session_data = None
        if token:
            session_data = auth_manager.validate_session(token)

        # Get request
        request_data = data.get('request')
        if not request_data:
            emit('mcp_response', {
                'error': 'Invalid request'
            })
            return

        # Handle request
        response = mcp_handler.handle_request(request_data, session_data)
        emit('mcp_response', response)

    @socketio.on('tool_execute')
    def handle_tool_execute(data):
        """Handle tool execution over WebSocket"""
        # Validate session
        token = data.get('token')
        if not token:
            emit('tool_result', {'error': 'Unauthorized'})
            return

        session_data = auth_manager.validate_session(token)
        if not session_data:
            emit('tool_result', {'error': 'Invalid token'})
            return

        # Get tool and arguments
        tool_name = data.get('tool')
        arguments = data.get('arguments', {})

        # Check access
        if not auth_manager.has_tool_access(session_data, tool_name):
            emit('tool_result', {'error': 'Access denied'})
            return

        # Execute tool
        try:
            tool = tools_registry.get_tool(tool_name)
            if not tool:
                emit('tool_result', {'error': 'Tool not found'})
                return

            result = tool.execute_with_tracking(arguments)
            emit('tool_result', {
                'success': True,
                'result': result
            })
        except Exception as e:
            emit('tool_result', {
                'success': False,
                'error': str(e)
            })

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)