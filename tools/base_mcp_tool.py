"""
Base class for MCP tools
"""
import json
import time
from typing import Dict, Any, List, Optional
from collections import deque
from datetime import datetime
import threading


class BaseMCPTool:
    """Base class for all MCP tools"""

    def __init__(self, config_path: str):
        """
        Initialize the MCP tool with configuration

        Args:
            config_path: Path to the JSON configuration file
        """
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.name = self.config.get('name', 'unnamed_tool')
        self.module = self.config.get('module', '')
        self.max_hits = self.config.get('max_hits', 1000)
        self.max_hit_interval = self.config.get('max_hit_interval', 10)
        self.tool_description = self.config.get('tool_description', {})

        # Tracking variables
        self.call_history = deque(maxlen=50)  # Last 50 calls
        self.error_history = deque(maxlen=50)  # Last 50 errors
        self.call_count = 0
        self.rate_limiter = deque()  # For rate limiting
        self._lock = threading.RLock()

        # Initialize tool-specific components
        self._initialize()

    def _initialize(self):
        """Override in subclasses for tool-specific initialization"""
        pass

    def check_rate_limit(self) -> bool:
        """
        Check if the rate limit has been exceeded

        Returns:
            True if rate limit exceeded, False otherwise
        """
        with self._lock:
            current_time = time.time()

            # Remove old entries outside the interval window
            while self.rate_limiter and self.rate_limiter[0] < current_time - self.max_hit_interval:
                self.rate_limiter.popleft()

            # Check if we've exceeded max_hits
            if len(self.rate_limiter) >= self.max_hits:
                return True

            # Add current request
            self.rate_limiter.append(current_time)
            return False

    def record_call(self, method_name: str, arguments: Dict[str, Any], result: Any = None, error: str = None):
        """
        Record a tool call for monitoring

        Args:
            method_name: Name of the method called
            arguments: Arguments passed to the method
            result: Result of the call (if successful)
            error: Error message (if failed)
        """
        with self._lock:
            self.call_count += 1

            call_record = {
                'timestamp': datetime.now().isoformat(),
                'method': method_name,
                'arguments': arguments,
                'call_number': self.call_count
            }

            if error:
                call_record['error'] = error
                self.error_history.append(call_record)
            else:
                call_record['result'] = str(result)[:200] if result else None  # Truncate large results

            self.call_history.append(call_record)

    def get_tools_definition(self) -> List[Dict[str, Any]]:
        """
        Get MCP tools definition for this tool

        Returns:
            List of tool definitions in MCP format
        """
        return self.tool_description.get('tools', [])

    def get_resources_definition(self) -> List[Dict[str, Any]]:
        """
        Get MCP resources definition for this tool

        Returns:
            List of resource definitions in MCP format
        """
        return self.tool_description.get('resources', [])

    def get_prompts_definition(self) -> List[Dict[str, Any]]:
        """
        Get MCP prompts definition for this tool

        Returns:
            List of prompt definitions in MCP format
        """
        return self.tool_description.get('prompts', [])

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a tool call - override in subclasses

        Args:
            tool_name: Name of the tool being called
            arguments: Arguments for the tool

        Returns:
            Result of the tool call
        """
        raise NotImplementedError("Subclasses must implement handle_tool_call")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics for this tool

        Returns:
            Dictionary of statistics
        """
        with self._lock:
            current_time = time.time()

            # Calculate calls per minute
            while self.rate_limiter and self.rate_limiter[0] < current_time - 60:
                self.rate_limiter.popleft()

            calls_per_minute = len(self.rate_limiter)

            return {
                'name': self.name,
                'total_calls': self.call_count,
                'calls_per_minute': calls_per_minute,
                'recent_calls': list(self.call_history),
                'recent_errors': list(self.error_history),
                'error_count': len(self.error_history)
            }