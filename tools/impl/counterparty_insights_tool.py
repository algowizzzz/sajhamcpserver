"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Counterparty Insights MCP Tool Implementation

This tool aggregates news and insights about any counterparty (bank, company, entity)
from configurable sources using the Tavily search tool with domain-specific queries.
"""

import json
from typing import Dict, Any, List
from ..base_mcp_tool import BaseMCPTool
from .tavily_tool import TavilyTool


class CounterpartyInsightsTool(BaseMCPTool):
    """
    Composite tool that aggregates counterparty insights from configurable sources
    using domain-filtered Tavily searches
    """
    
    def __init__(self, config: Dict = None):
        """Initialize Counterparty Insights tool"""
        default_config = {
            'name': 'counterparty_insights',
            'description': 'Aggregate counterparty insights from configurable sources',
            'version': '1.0.0',
            'enabled': True
        }
        if config:
            default_config.update(config)
        super().__init__(default_config)
        
        # Load sources from config
        self.sources = config.get('sources', {}) if config else {}
        
        # Initialize Tavily tool for searches
        tavily_config_path = 'config/tools/tavily.json'
        try:
            with open(tavily_config_path, 'r') as f:
                tavily_config = json.load(f)
            self.tavily = TavilyTool(tavily_config)
        except Exception as e:
            self.logger.error(f"Failed to initialize Tavily tool: {e}")
            self.tavily = None
    
    def get_input_schema(self) -> Dict:
        """Get input schema for Counterparty Insights tool"""
        # Get available categories from config
        categories = list(self.sources.keys()) if self.sources else []
        
        return {
            "type": "object",
            "properties": {
                "counterparty_name": {
                    "type": "string",
                    "description": "Full name of the counterparty/entity (e.g., 'Royal Bank of Canada')",
                },
                "counterparty_short_name": {
                    "type": "string",
                    "description": "Short name or ticker (e.g., 'RBC')",
                },
                "categories": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": categories + ["all"] if categories else ["all"]
                    },
                    "description": "News categories to fetch (default: all)",
                    "default": ["all"]
                },
                "max_results_per_source": {
                    "type": "integer",
                    "description": "Maximum results per source",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 10
                },
                "search_depth": {
                    "type": "string",
                    "description": "Search depth",
                    "enum": ["basic", "advanced"],
                    "default": "advanced"
                },
                "include_summary": {
                    "type": "boolean",
                    "description": "Include AI summary for each source",
                    "default": True
                },
                "include_full_content": {
                    "type": "boolean",
                    "description": "Fetch full article content (raw HTML/text)",
                    "default": False
                }
            },
            "required": ["counterparty_name", "counterparty_short_name"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Any:
        """
        Execute counterparty insights aggregation
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Aggregated insights from multiple sources
        """
        if not self.tavily:
            raise RuntimeError("Tavily tool not initialized")
        
        counterparty_name = arguments.get('counterparty_name')
        counterparty_short = arguments.get('counterparty_short_name')
        
        if not counterparty_name or not counterparty_short:
            raise ValueError("Both counterparty_name and counterparty_short_name are required")
        
        categories = arguments.get('categories', ['all'])
        max_results = arguments.get('max_results_per_source', 3)
        search_depth = arguments.get('search_depth', 'advanced')
        include_summary = arguments.get('include_summary', True)
        include_full_content = arguments.get('include_full_content', False)
        
        # Expand "all" to all categories
        if 'all' in categories:
            categories = list(self.sources.keys())
        
        results = {
            'counterparty': {
                'full_name': counterparty_name,
                'short_name': counterparty_short
            },
            'query': f'{counterparty_short} / {counterparty_name} Insights Aggregation',
            'categories_searched': categories,
            'total_sources': 0,
            'total_articles': 0,
            'by_category': {}
        }
        
        # Search each category
        for category in categories:
            if category not in self.sources:
                self.logger.warning(f"Category '{category}' not found in config")
                continue
            
            category_config = self.sources[category]
            category_results = {
                'description': category_config.get('description', f'{category} sources'),
                'sources': {}
            }
            
            # Search each source in category
            for source_key, source_config in category_config.get('sources', {}).items():
                try:
                    source_results = self._search_source(
                        source_config,
                        counterparty_name,
                        counterparty_short,
                        max_results,
                        search_depth,
                        include_summary,
                        include_full_content
                    )
                    
                    if source_results and source_results.get('results_count', 0) > 0:
                        category_results['sources'][source_key] = source_results
                        results['total_sources'] += 1
                        results['total_articles'] += source_results['results_count']
                    
                except Exception as e:
                    self.logger.error(f"Error searching {source_key}: {e}")
                    category_results['sources'][source_key] = {
                        'error': str(e),
                        'domain': source_config.get('domain', 'unknown')
                    }
            
            if category_results['sources']:
                results['by_category'][category] = category_results
        
        return results
    
    def _search_source(
        self,
        source_config: Dict,
        counterparty_name: str,
        counterparty_short: str,
        max_results: int,
        search_depth: str,
        include_summary: bool,
        include_full_content: bool
    ) -> Dict:
        """
        Search a single source using Tavily
        
        Args:
            source_config: Source configuration
            counterparty_name: Full counterparty name
            counterparty_short: Short counterparty name
            max_results: Max results to return
            search_depth: Search depth
            include_summary: Include AI summary
            include_full_content: Include full article content
            
        Returns:
            Search results
        """
        # Build query by substituting placeholders
        query_template = source_config.get('query_template', '')
        query = query_template.replace('{FULL_NAME}', counterparty_name)
        query = query.replace('{SHORT_NAME}', counterparty_short)
        
        tavily_args = {
            'query': query,
            'topic': source_config.get('topic', 'finance'),
            'search_depth': search_depth,
            'max_results': max_results,
            'include_answer': include_summary,
            'include_raw_content': include_full_content,
            'include_domains': [source_config['domain']]
        }
        
        result = self.tavily.execute(tavily_args)
        
        # Add source metadata
        result['source_name'] = source_config.get('description', source_config['domain'])
        result['domain'] = source_config['domain']
        result['query_used'] = query
        
        return result

