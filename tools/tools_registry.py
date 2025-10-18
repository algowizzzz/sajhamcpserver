"""
Tools Registry for managing and monitoring MCP tools
"""
import os
import json
import threading
import time
import importlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from collections import deque


class ToolsRegistry:
    """Singleton class for managing MCP tools"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_folder: str = 'config/tools',
                 reload_interval: int = 300,
                 max_call_history: int = 50,
                 max_error_history: int = 50):
        """
        Initialize the ToolsRegistry

        Args:
            config_folder: Folder containing tool configuration files
            reload_interval: Interval in seconds for checking config changes
            max_call_history: Maximum number of calls to track per tool
            max_error_history: Maximum number of errors to track per tool
        """
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.config_folder = config_folder
        self.reload_interval = reload_interval
        self.max_call_history = max_call_history
        self.max_error_history = max_error_history

        # Storage for tools and configurations
        self.tools = {}  # tool_name -> tool_instance
        self.tool_configs = {}  # tool_name -> config
        self.tool_timestamps = {}  # config_file -> last_modified

        # Global tracking
        self.global_call_history = deque(maxlen=max_call_history * 10)
        self.global_error_history = deque(maxlen=max_error_history * 10)

        # Thread safety
        self._registry_lock = threading.RLock()
        self._stop_monitor = threading.Event()

        # Create config folder if it doesn't exist
        os.makedirs(config_folder, exist_ok=True)

        # Load all tools
        self._load_all_tools()

        # Start monitoring thread
        self._monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
        self._monitor_thread.start()

    def _load_all_tools(self):
        """Load all tools from configuration files"""
        config_files = Path(self.config_folder).glob('*.json')

        for config_file in config_files:
            try:
                self._load_tool_from_config(config_file)
            except Exception as e:
                print(f"Error loading tool from {config_file}: {e}")

    def _load_tool_from_config(self, config_file: Path):
        """
        Load a single tool from its configuration file

        Args:
            config_file: Path to the configuration file
        """
        with self._registry_lock:
            # Check if file has been modified
            current_mtime = config_file.stat().st_mtime
            last_mtime = self.tool_timestamps.get(str(config_file), 0)

            if current_mtime <= last_mtime and str(config_file) in self.tool_timestamps:
                return  # File hasn't changed

            # Load configuration
            with open(config_file, 'r') as f:
                config = json.load(f)

            tool_name = config.get('name', '')
            module_path = config.get('module', '')

            if not tool_name or not module_path:
                print(f"Invalid configuration in {config_file}")
                return

            try:
                # Unload existing tool if present
                if tool_name in self.tools:
                    self._unload_tool(tool_name)

                # Parse module and class from path
                parts = module_path.rsplit('.', 1)
                if len(parts) == 2:
                    module_name, class_name = parts
                else:
                    module_name = module_path
                    # Guess class name from tool name
                    class_name = ''.join(word.capitalize() for word in tool_name.split('_'))

                # Import module and get class
                module = importlib.import_module(module_name)

                # Reload module if already imported (for hot-reload)
                importlib.reload(module)

                tool_class = getattr(module, class_name)

                # Instantiate tool
                tool_instance = tool_class(str(config_file))

                # Register tool
                self.tools[tool_name] = tool_instance
                self.tool_configs[tool_name] = config
                self.tool_timestamps[str(config_file)] = current_mtime

                print(f"Loaded tool: {tool_name} from {config_file}")

            except Exception as e:
                print(f"Error loading tool {tool_name}: {e}")
                # Record error
                self.global_error_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'tool': tool_name,
                    'error': f"Failed to load: {str(e)}",
                    'config_file': str(config_file)
                })

    def _unload_tool(self, tool_name: str):
        """
        Unload a tool from the registry

        Args:
            tool_name: Name of the tool to unload
        """
        with self._registry_lock:
            if tool_name in self.tools:
                # Clean up tool resources if needed
                tool = self.tools[tool_name]
                if hasattr(tool, 'cleanup'):
                    try:
                        tool.cleanup()
                    except:
                        pass

                # Remove from registry
                del self.tools[tool_name]

                if tool_name in self.tool_configs:
                    del self.tool_configs[tool_name]

                print(f"Unloaded tool: {tool_name}")

    def _monitor_worker(self):
        """Worker thread for monitoring configuration changes"""
        while not self._stop_monitor.wait(self.reload_interval):
            try:
                self._check_config_changes()
            except Exception as e:
                print(f"Error in monitor worker: {e}")

    def _check_config_changes(self):
        """Check for configuration file changes"""
        with self._registry_lock:
            config_files = set(Path(self.config_folder).glob('*.json'))
            current_files = set(self.tool_timestamps.keys())

            # Convert Path objects to strings for comparison
            config_files_str = {str(f) for f in config_files}

            # Check for new files
            new_files = config_files_str - current_files
            for file_path in new_files:
                print(f"Detected new config file: {file_path}")
                self._load_tool_from_config(Path(file_path))

            # Check for removed files
            removed_files = current_files - config_files_str
            for file_path in removed_files:
                # Find and unload corresponding tool
                for tool_name, config in self.tool_configs.items():
                    if str(file_path).endswith(f"{tool_name}.json"):
                        print(f"Detected removed config file: {file_path}")
                        self._unload_tool(tool_name)
                        break

                if file_path in self.tool_timestamps:
                    del self.tool_timestamps[file_path]

            # Check for modified files
            for config_file in config_files:
                self._load_tool_from_config(config_file)

    def get_tool(self, tool_name: str) -> Optional[Any]:
        """
        Get a tool instance by name

        Args:
            tool_name: Name of the tool

        Returns:
            Tool instance or None
        """
        with self._registry_lock:
            return self.tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """
        Get list of all available tools

        Returns:
            List of tool names
        """
        with self._registry_lock:
            return list(self.tools.keys())

    def get_tool_config(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a tool

        Args:
            tool_name: Name of the tool

        Returns:
            Tool configuration or None
        """
        with self._registry_lock:
            return self.tool_configs.get(tool_name)

    def handle_tool_call(self, tool_name: str, method_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a tool call through the registry

        Args:
            tool_name: Name of the tool
            method_name: Method to call on the tool
            arguments: Arguments for the method

        Returns:
            Result of the tool call
        """
        with self._registry_lock:
            tool = self.get_tool(tool_name)

            if not tool:
                error_msg = f"Tool '{tool_name}' not found"
                self._record_error(tool_name, method_name, arguments, error_msg)
                return {"error": error_msg, "status": 404}

            try:
                # Check rate limit
                config = self.tool_configs.get(tool_name, {})
                max_hits = config.get('max_hits', 1000)
                max_hit_interval = config.get('max_hit_interval', 10)

                # Call tool method
                result = tool.handle_tool_call(method_name, arguments)

                # Record successful call
                self._record_call(tool_name, method_name, arguments, result)

                return result

            except Exception as e:
                error_msg = str(e)
                self._record_error(tool_name, method_name, arguments, error_msg)
                return {"error": error_msg, "status": 500}

    def _record_call(self, tool_name: str, method_name: str, arguments: Dict[str, Any], result: Any):
        """Record a successful tool call"""
        call_record = {
            'timestamp': datetime.now().isoformat(),
            'tool': tool_name,
            'method': method_name,
            'arguments': arguments,
            'success': True
        }

        self.global_call_history.append(call_record)

    def _record_error(self, tool_name: str, method_name: str, arguments: Dict[str, Any], error: str):
        """Record a failed tool call"""
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'tool': tool_name,
            'method': method_name,
            'arguments': arguments,
            'error': error
        }

        self.global_error_history.append(error_record)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get global statistics for all tools

        Returns:
            Dictionary of statistics
        """
        with self._registry_lock:
            tool_stats = {}

            for tool_name, tool in self.tools.items():
                if hasattr(tool, 'get_stats'):
                    tool_stats[tool_name] = tool.get_stats()

            return {
                'tools_loaded': len(self.tools),
                'tool_names': list(self.tools.keys()),
                'global_call_count': len(self.global_call_history),
                'global_error_count': len(self.global_error_history),
                'recent_calls': list(self.global_call_history)[-10:],
                'recent_errors': list(self.global_error_history)[-10:],
                'tool_statistics': tool_stats
            }

    def get_tool_statistics(self, tool_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific tool

        Args:
            tool_name: Name of the tool

        Returns:
            Tool statistics
        """
        with self._registry_lock:
            tool = self.get_tool(tool_name)

            if not tool:
                return {"error": f"Tool '{tool_name}' not found"}

            if hasattr(tool, 'get_stats'):
                return tool.get_stats()
            else:
                return {"error": "Tool does not support statistics"}

    def get_mcp_definitions(self) -> Dict[str, Any]:
        """
        Get MCP definitions for all tools

        Returns:
            Combined MCP definitions
        """
        with self._registry_lock:
            all_tools = []
            all_resources = []
            all_prompts = []

            for tool_name, tool in self.tools.items():
                if hasattr(tool, 'get_tools_definition'):
                    tools_def = tool.get_tools_definition()
                    # Add tool name prefix to avoid conflicts
                    for t in tools_def:
                        t['name'] = f"{tool_name}.{t.get('name', '')}"
                    all_tools.extend(tools_def)

                if hasattr(tool, 'get_resources_definition'):
                    all_resources.extend(tool.get_resources_definition())

                if hasattr(tool, 'get_prompts_definition'):
                    all_prompts.extend(tool.get_prompts_definition())

            return {
                'tools': all_tools,
                'resources': all_resources,
                'prompts': all_prompts
            }

    def reload_tool(self, tool_name: str) -> bool:
        """
        Force reload a specific tool

        Args:
            tool_name: Name of the tool to reload

        Returns:
            True if successful, False otherwise
        """
        with self._registry_lock:
            # Find config file for the tool
            config_file = None
            for file_path in Path(self.config_folder).glob('*.json'):
                if file_path.stem == tool_name or file_path.stem == f"{tool_name}_tool":
                    config_file = file_path
                    break

            if not config_file:
                return False

            # Force reload by removing timestamp
            if str(config_file) in self.tool_timestamps:
                del self.tool_timestamps[str(config_file)]

            # Reload tool
            try:
                self._load_tool_from_config(config_file)
                return True
            except Exception as e:
                print(f"Error reloading tool {tool_name}: {e}")
                return False

    def stop(self):
        """Stop the registry and clean up resources"""
        self._stop_monitor.set()

        if hasattr(self, '_monitor_thread'):
            self._monitor_thread.join(timeout=5)

        # Unload all tools
        with self._registry_lock:
            tool_names = list(self.tools.keys())
            for tool_name in tool_names:
                self._unload_tool(tool_name)