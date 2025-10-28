"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Adapter to use MCP tools with LangGraph
"""
from typing import Dict, List, Any, Optional
from tools.tools_registry import ToolsRegistry
import logging
import json


class MCPToolsAdapter:
    """Adapter to integrate MCP tools with LangGraph agents"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.registry = ToolsRegistry()
        self.config = config or {}
        
        # Get enabled tools based on agent config
        self.enabled_tool_names = self.config.get('enabled_tools', [])
        
        # If no specific tools listed, use all
        if not self.enabled_tool_names:
            all_tools = self.registry.get_all_tools()
            self.enabled_tool_names = [t['name'] for t in all_tools]
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with descriptions"""
        tools = []
        
        for tool_name in self.enabled_tool_names:
            tool = self.registry.get_tool(tool_name)
            if tool and tool.enabled:
                tools.append({
                    'name': tool.name,
                    'description': tool.description,
                    'input_schema': tool.get_input_schema()
                })
        
        return tools
    
    def get_tools_description(self) -> str:
        """Get formatted description of all available tools"""
        tools = self.get_available_tools()
        
        descriptions = []
        for tool in tools:
            desc = f"- **{tool['name']}**: {tool['description']}\n"
            
            # Add required parameters
            schema = tool['input_schema']
            if 'required' in schema and schema['required']:
                desc += f"  Required: {', '.join(schema['required'])}\n"
            
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool and return results"""
        try:
            tool = self.registry.get_tool(tool_name)
            if not tool:
                return {
                    'error': f"Tool '{tool_name}' not found",
                    'available_tools': [t['name'] for t in self.get_available_tools()]
                }
            
            if not tool.enabled:
                return {
                    'error': f"Tool '{tool_name}' is disabled"
                }
            
            self.logger.info(f"Executing tool: {tool_name} with args: {arguments}")
            result = tool.execute(arguments)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                'error': str(e),
                'tool': tool_name,
                'arguments': arguments
            }
    
    def format_tool_result(self, result: Any, max_length: int = 2000) -> str:
        """Format tool result for LLM consumption"""
        if isinstance(result, dict):
            result_str = json.dumps(result, indent=2, default=str)
        else:
            result_str = str(result)
        
        # Truncate if too long
        if len(result_str) > max_length:
            result_str = result_str[:max_length] + "\n... (truncated)"
        
        return result_str

