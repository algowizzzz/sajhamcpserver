#!/usr/bin/env python3
"""
Main entry point for the MCP Server application
"""
import os
import sys
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.tools_registry import ToolsRegistry
from web.mcp_app import create_app
from core.properties_configurator import PropertiesConfigurator


def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/mcp_server.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'config',
        'config/tools',
        'data',
        'data/office_files',
        'logs',
        'instance'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("✓ Created necessary directories")


def create_default_configs():
    """Create default configuration files if they don't exist"""
    # Create users.json
    users_file = 'config/users.json'
    if not os.path.exists(users_file):
        default_users = {
            "users": [
                {
                    "id": "admin",
                    "password": "admin123",
                    "full_name": "Administrator",
                    "roles": ["admin", "user"]
                },
                {
                    "id": "user1",
                    "password": "user123",
                    "full_name": "John Doe",
                    "roles": ["user"]
                }
            ]
        }

        import json
        with open(users_file, 'w') as f:
            json.dump(default_users, f, indent=2)

        print("✓ Created default users configuration")

    # Create application.properties
    props_file = 'config/application.properties'
    if not os.path.exists(props_file):
        default_props = """# MCP Server Configuration
server.host=0.0.0.0
server.port=5000
server.debug=False

# Flask Configuration
flask.secret_key=${FLASK_SECRET_KEY:default_secret_key_change_in_production}

# Tool Registry Configuration
registry.config_folder=config/tools
registry.reload_interval=300
registry.max_call_history=50
registry.max_error_history=50

# Database Configuration
sql.db_path=data/sample.db
duckdb.data_folder=data

# Office Files Configuration
office.data_folder=data/office_files

# API Keys (set as environment variables)
google.api_key=${GOOGLE_API_KEY:}
google.cse_id=${GOOGLE_CSE_ID:}
tavily.api_key=${TAVILY_API_KEY:}
fred.api_key=${FRED_API_KEY:}
census.api_key=${CENSUS_API_KEY:}
sec.user_agent=${SEC_USER_AGENT:YourApp/1.0}
"""

        with open(props_file, 'w') as f:
            f.write(default_props)

        print("✓ Created default application properties")


def create_sample_tool_configs():
    """Check if sample tool configuration files exist"""
    import json

    # Check SQL config
    sql_config_file = 'config/tools/sql_mcp_tool.json'
    if not os.path.exists(sql_config_file):
        print("⚠ SQL tool configuration not found. Please ensure sql_mcp_tool.json is in config/tools/")
    else:
        print("✓ SQL tool configuration found")

    # Check DuckDB config
    duckdb_config_file = 'config/tools/duckdb_olap_mcp_tool.json'
    if not os.path.exists(duckdb_config_file):
        print("⚠ DuckDB tool configuration not found. Please ensure duckdb_olap_mcp_tool.json is in config/tools/")
    else:
        print("✓ DuckDB tool configuration found")


def main():
    """Main entry point"""
    print("=" * 60)
    print("MCP Server - Model Context Protocol Server")
    print("© 2025-2030 Ashutosh Sinha")
    print("=" * 60)
    print()

    # Setup
    print("Setting up MCP Server...")
    create_directories()
    create_default_configs()
    create_sample_tool_configs()

    # Setup logging
    logger = setup_logging()
    logger.info("Starting MCP Server...")

    # Load properties
    print("\n✓ Loading application properties...")
    props = PropertiesConfigurator(['config/application.properties'])

    # Set environment variables from properties
    if props.get('google.api_key'):
        os.environ['GOOGLE_API_KEY'] = props.get('google.api_key')
    if props.get('tavily.api_key'):
        os.environ['TAVILY_API_KEY'] = props.get('tavily.api_key')
    if props.get('fred.api_key'):
        os.environ['FRED_API_KEY'] = props.get('fred.api_key')
    if props.get('census.api_key'):
        os.environ['CENSUS_API_KEY'] = props.get('census.api_key')
    if props.get('sec.user_agent'):
        os.environ['SEC_USER_AGENT'] = props.get('sec.user_agent')

    # Initialize Tools Registry
    print("\n✓ Initializing Tools Registry...")
    registry = ToolsRegistry(
        config_folder=props.get('registry.config_folder', 'config/tools'),
        reload_interval=props.get_int('registry.reload_interval', 300),
        max_call_history=props.get_int('registry.max_call_history', 50),
        max_error_history=props.get_int('registry.max_error_history', 50)
    )

    # List loaded tools
    tools = registry.list_tools()
    print(f"\n✓ Loaded {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool}")

    # Create and run Flask app
    print("\n✓ Starting Flask web server...")
    app = create_app()

    # Get server configuration
    host = props.get('server.host', '0.0.0.0')
    port = props.get_int('server.port', 5000)
    debug = props.get('server.debug', 'False').lower() == 'true'

    print(f"\n{'=' * 60}")
    print(f"MCP Server is running!")
    print(f"Access the dashboard at: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    print(f"Default credentials:")
    print(f"  Admin: admin / admin123")
    print(f"  User:  user1 / user123")
    print(f"{'=' * 60}\n")

    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\nShutting down MCP Server...")
        registry.stop()
        print("Goodbye!")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        raise


if __name__ == '__main__':
    main()