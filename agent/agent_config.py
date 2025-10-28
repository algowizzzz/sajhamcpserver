"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Agent Configuration Management
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class AgentConfig:
    """Load and manage agent configurations"""
    
    def __init__(self, config_dir: str = 'config/agents'):
        self.config_dir = config_dir
        self.logger = logging.getLogger(__name__)
        os.makedirs(self.config_dir, exist_ok=True)
    
    def load_agent_config(self, agent_name: str = 'default_agent') -> Dict[str, Any]:
        """Load agent configuration from JSON file"""
        config_file = Path(self.config_dir) / f"{agent_name}.json"
        
        if not config_file.exists():
            self.logger.warning(f"Config file not found: {config_file}, using defaults")
            return self._get_default_config()
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            self.logger.info(f"Loaded agent config: {agent_name}")
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading config {config_file}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default agent configuration"""
        return {
            "name": "default_agent",
            "description": "General purpose assistant agent",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_iterations": 5,
            "enabled_tools": [],  # Empty means all tools
            "system_prompt_template": "default",
            "response_format": "natural",
            "streaming": False,
            "metadata": {
                "version": "1.0.0",
                "author": "System"
            }
        }
    
    def list_available_agents(self) -> list:
        """List all available agent configurations"""
        config_path = Path(self.config_dir)
        agents = []
        
        for config_file in config_path.glob('*.json'):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    agents.append({
                        'name': config.get('name', config_file.stem),
                        'description': config.get('description', 'No description'),
                        'tools_count': len(config.get('enabled_tools', [])) or 'all'
                    })
            except Exception as e:
                self.logger.error(f"Error reading {config_file}: {e}")
        
        return agents
    
    def save_agent_config(self, config: Dict[str, Any]) -> bool:
        """Save agent configuration to JSON file"""
        try:
            agent_name = config.get('name', 'unnamed_agent')
            config_file = Path(self.config_dir) / f"{agent_name}.json"
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Saved agent config: {agent_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False

