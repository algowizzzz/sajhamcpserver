"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
LangGraph-based Agent Executor
"""
from typing import Dict, Any, List
import re
import json
import logging

from .state import AgentState
from .tools_adapter import MCPToolsAdapter
from .prompts import get_system_prompt


class AgentExecutor:
    """Simple agent that uses MCP tools (LangGraph-ready structure)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize tools adapter
        tools_config = config.get('tools', {})
        tools_config['enabled_tools'] = tools_config.get('enabled', [])
        self.tools = MCPToolsAdapter(tools_config)
        
        # Get system prompt (from config or fallback to templates)
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt from config or fallback to templates"""
        # Try to get prompt from config first (new way)
        if 'prompt' in self.config and 'system' in self.config['prompt']:
            prompt_template = self.config['prompt']['system']
            
            # Get max_iterations from execution config or top-level
            execution_config = self.config.get('execution', {})
            max_iterations = execution_config.get('max_iterations', 
                                                 self.config.get('max_iterations', 5))
            
            # Replace variables
            prompt = prompt_template.format(
                tools_description=self.tools.get_tools_description(),
                max_iterations=max_iterations
            )
            
            self.logger.info("Using prompt from agent config")
            return prompt
        
        # Fallback to old template-based approach (backward compatibility)
        template_name = self.config.get('system_prompt_template', 'default')
        max_iterations = self.config.get('max_iterations', 5)
        
        self.logger.info(f"Using prompt template: {template_name}")
        return get_system_prompt(
            template_name,
            self.tools.get_tools_description(),
            max_iterations
        )
    
    def run(self, query: str) -> Dict[str, Any]:
        """Execute the agent workflow"""
        # Initialize state
        state = {
            'query': query,
            'messages': [],
            'selected_tool': None,
            'tool_input': {},
            'tool_output': None,
            'thought': '',
            'observation': '',
            'iteration': 0,
            'max_iterations': self._get_max_iterations(),
            'final_answer': '',
            'agent_config': self.config
        }
        
        # Start the reasoning loop
        while state['iteration'] < state['max_iterations']:
            self.logger.info(f"Iteration {state['iteration'] + 1}/{state['max_iterations']}")
            
            # Think step
            state = self.think(state)
            
            # Check if we have a final answer
            if state.get('final_answer'):
                break
            
            # Act step (if tool selected)
            if state.get('selected_tool'):
                state = self.act(state)
                state = self.observe(state)
                state['iteration'] += 1
            else:
                # No tool selected, try to get final answer
                break
        
        # If no final answer yet, generate one
        if not state.get('final_answer'):
            state['final_answer'] = self._generate_final_answer(state)
        
        return {
            'query': query,
            'final_answer': state['final_answer'],
            'iterations': state['iteration'],
            'tools_used': self._get_tools_used(state),
            'success': True
        }
    
    def _get_max_iterations(self) -> int:
        """Get max iterations from config"""
        execution_config = self.config.get('execution', {})
        return execution_config.get('max_iterations', 
                                   self.config.get('max_iterations', 5))
    
    def think(self, state: AgentState) -> AgentState:
        """Agent reasoning step - uses simple pattern matching for now"""
        query = state['query'].lower()
        
        # Simple pattern matching to select tools
        # This is a simplified version - can be enhanced with LLM later
        
        if 'limit' in query or 'breach' in query or 'exposure' in query or 'counterparty' in query or 'risk' in query:
            # Extract counterparty name or code
            counterparty = self._extract_counterparty(state['query'])
            
            if counterparty:
                state['thought'] = f"User is asking about counterparty risk for {counterparty}. I should use the limits_exposure_analysis tool."
                state['selected_tool'] = 'limits_exposure_analysis'
                state['tool_input'] = {'counterparty_identifier': counterparty}
            else:
                state['thought'] = "User is asking about limits/risk but I need a counterparty name."
                state['final_answer'] = "Please specify which counterparty you'd like me to analyze. You can provide either the customer name (e.g., 'Northbridge Capital') or the Adaptiv code (e.g., 'AC001')."
        
        elif 'list' in query and ('table' in query or 'data' in query or 'file' in query):
            state['thought'] = "User wants to see available data tables. I should use duckdb_olap_tools to list tables."
            state['selected_tool'] = 'duckdb_olap_tools'
            state['tool_input'] = {'action': 'list_tables'}
        
        elif 'query' in query or 'select' in query or 'sql' in query:
            # Extract SQL query if present
            sql_query = self._extract_sql(state['query'])
            if sql_query:
                state['thought'] = f"User wants to execute a SQL query: {sql_query}"
                state['selected_tool'] = 'duckdb_olap_tools'
                state['tool_input'] = {'action': 'query', 'sql_query': sql_query}
            else:
                state['final_answer'] = "Please provide the SQL query you'd like me to execute."
        
        elif 'search' in query or 'google' in query:
            search_terms = self._extract_search_terms(state['query'])
            if search_terms:
                state['thought'] = f"User wants to search for: {search_terms}"
                state['selected_tool'] = 'tavily'
                state['tool_input'] = {'query': search_terms}
            else:
                state['final_answer'] = "Please specify what you'd like me to search for."
        
        elif 'wikipedia' in query or 'wiki' in query:
            search_terms = self._extract_search_terms(state['query'])
            if search_terms:
                state['thought'] = f"User wants Wikipedia information about: {search_terms}"
                state['selected_tool'] = 'wikipedia'
                state['tool_input'] = {'query': search_terms, 'action': 'search'}
            else:
                state['final_answer'] = "Please specify what you'd like me to look up on Wikipedia."
        
        elif 'insights' in query or 'intelligence' in query or 'research' in query or 'due diligence' in query or 'background' in query:
            # Extract company/entity name
            company_name = self._extract_company_name(state['query'])
            if company_name:
                # Try to extract short name/ticker
                short_name = company_name.split()[0] if company_name else company_name
                state['thought'] = f"User wants comprehensive insights about {company_name}. I should use the counterparty_insights tool."
                state['selected_tool'] = 'counterparty_insights'
                state['tool_input'] = {
                    'counterparty_name': company_name,
                    'counterparty_short_name': short_name,
                    'categories': ['all'],
                    'search_depth': 'advanced',
                    'include_summary': True,
                    'max_results_per_source': 5
                }
            else:
                state['final_answer'] = "Please specify which company or entity you'd like me to research."
        
        else:
            # Default: provide guidance
            state['final_answer'] = self._get_help_message()
        
        return state
    
    def act(self, state: AgentState) -> AgentState:
        """Execute tool action"""
        tool_name = state['selected_tool']
        tool_input = state['tool_input']
        
        self.logger.info(f"Executing tool: {tool_name}")
        self.logger.debug(f"Tool input: {tool_input}")
        
        try:
            # Execute tool
            result = self.tools.execute_tool(tool_name, tool_input)
            state['tool_output'] = result
            
        except Exception as e:
            self.logger.error(f"Tool execution error: {e}")
            state['tool_output'] = {'error': str(e)}
        
        return state
    
    def observe(self, state: AgentState) -> AgentState:
        """Process tool output and generate response"""
        tool_output = state['tool_output']
        tool_name = state['selected_tool']
        
        # Format observation based on tool type
        if tool_name == 'limits_exposure_analysis':
            state['final_answer'] = self._format_risk_analysis(tool_output)
        
        elif tool_name == 'duckdb_olap_tools':
            state['final_answer'] = self._format_data_analysis(tool_output, state['tool_input'])
        
        elif tool_name in ['tavily', 'google_search']:
            state['final_answer'] = self._format_search_results(tool_output)
        
        elif tool_name == 'wikipedia':
            state['final_answer'] = self._format_wikipedia_results(tool_output)
        
        elif tool_name == 'counterparty_insights':
            state['final_answer'] = self._format_counterparty_insights(tool_output)
        
        else:
            # Generic formatting
            state['final_answer'] = self._format_generic_result(tool_output)
        
        state['observation'] = f"Tool {tool_name} completed successfully"
        
        return state
    
    def _extract_counterparty(self, text: str) -> str:
        """Extract counterparty name or code from text"""
        # Look for AC### pattern (Adaptiv codes)
        ac_match = re.search(r'\bAC\d{3}\b', text, re.IGNORECASE)
        if ac_match:
            return ac_match.group(0).upper()
        
        # Look for known counterparty names
        known_counterparties = [
            'Northbridge Capital', 'Lakeview Partners', 'Aurora Metals',
            'Blue River Bank', 'Pacific Energy', 'Metro Capital'
        ]
        
        for cp in known_counterparties:
            if cp.lower() in text.lower():
                return cp
        
        # Try to extract capitalized words that might be a company name
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and i + 1 < len(words) and words[i + 1][0].isupper():
                return f"{word} {words[i + 1]}"
        
        return None
    
    def _extract_sql(self, text: str) -> str:
        """Extract SQL query from text"""
        # Look for SELECT statement
        match = re.search(r'SELECT\s+.+?(?:FROM|$)', text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(0).strip()
        return None
    
    def _extract_search_terms(self, text: str) -> str:
        """Extract search terms from query"""
        # Remove common words
        text = re.sub(r'\b(search|google|wikipedia|wiki|for|about|find|lookup|look up)\b', '', text, flags=re.IGNORECASE)
        return text.strip()
    
    def _extract_company_name(self, text: str) -> str:
        """Extract company/entity name from query"""
        # Remove action words
        text = re.sub(r'\b(insights?|intelligence|research|due diligence|background|about|on|for|analyze|get)\b', '', text, flags=re.IGNORECASE)
        return text.strip()
    
    def _format_risk_analysis(self, result: Dict[str, Any]) -> str:
        """Format risk analysis results"""
        if 'error' in result:
            return f"Error analyzing counterparty: {result['error']}"
        
        summary = result.get('summary', {})
        
        response = f"# Risk Analysis: {summary.get('customer_name', 'Unknown')}\n\n"
        response += "## Executive Summary\n"
        response += f"- **Rating**: {summary.get('rating', 'N/A')}\n"
        response += f"- **Sector**: {summary.get('sector', 'N/A')}\n"
        response += f"- **Limit Status**: {summary.get('limit_status', 'N/A')}\n"
        response += f"- **Utilization**: {summary.get('limit_utilization_pct', 0):.2f}%\n\n"
        
        response += "## Exposure Metrics\n"
        response += f"- **Exposure (EPE)**: ${summary.get('exposure_epe', 0):,.2f}\n"
        response += f"- **Total Trades**: {summary.get('total_trades', 0)}\n"
        response += f"- **Total Notional**: ${summary.get('total_notional', 0):,.2f}\n"
        response += f"- **Total MTM**: ${summary.get('total_mtm', 0):,.2f}\n"
        response += f"- **Total P&L**: ${summary.get('total_pnl', 0):,.2f}\n"
        response += f"- **Failed Trades**: {summary.get('failed_trades_count', 0)}\n\n"
        
        # Add breach warning if applicable
        if summary.get('limit_status') == 'BREACH':
            response += "⚠️  **WARNING**: This counterparty has breached their credit limit!\n\n"
        elif summary.get('limit_status') == 'WARNING':
            response += "🟡 **CAUTION**: This counterparty is approaching their credit limit.\n\n"
        
        return response
    
    def _format_data_analysis(self, result: Dict[str, Any], tool_input: Dict[str, Any]) -> str:
        """Format data analysis results"""
        if 'error' in result:
            return f"Error executing query: {result['error']}"
        
        action = tool_input.get('action')
        
        if action == 'list_tables':
            response = "# Available Data Tables\n\n"
            for table in result.get('tables', []):
                response += f"- **{table['name']}**: {table['row_count']} rows\n"
            response += f"\nTotal: {result.get('table_count', 0)} tables\n"
            return response
        
        elif action == 'query':
            response = f"# Query Results\n\n"
            response += f"**Query**: `{tool_input.get('sql_query')}`\n\n"
            response += f"**Rows Returned**: {result.get('row_count', 0)}\n\n"
            
            if result.get('row_count', 0) > 0:
                response += "**Results**:\n```\n"
                # Show first few rows
                for i, row in enumerate(result.get('rows', [])[:10]):
                    response += f"{row}\n"
                if result.get('row_count', 0) > 10:
                    response += f"... ({result.get('row_count') - 10} more rows)\n"
                response += "```\n"
            
            return response
        
        return json.dumps(result, indent=2, default=str)
    
    def _format_search_results(self, result: Dict[str, Any]) -> str:
        """Format search results"""
        if 'error' in result:
            return f"Search error: {result['error']}"
        
        response = "# Search Results\n\n"
        
        results = result.get('results', [])
        for i, item in enumerate(results[:5], 1):
            response += f"## {i}. {item.get('title', 'No title')}\n"
            response += f"{item.get('snippet', item.get('description', 'No description'))}\n"
            response += f"Source: {item.get('url', item.get('link', 'No URL'))}\n\n"
        
        return response
    
    def _format_wikipedia_results(self, result: Dict[str, Any]) -> str:
        """Format Wikipedia results"""
        if 'error' in result:
            return f"Wikipedia error: {result['error']}"
        
        response = f"# Wikipedia: {result.get('title', 'Unknown')}\n\n"
        response += result.get('summary', result.get('content', 'No content available'))[:1000]
        
        if result.get('url'):
            response += f"\n\nFull article: {result['url']}"
        
        return response
    
    def _format_counterparty_insights(self, result: Dict[str, Any]) -> str:
        """Format counterparty insights results"""
        if 'error' in result:
            return f"Error gathering insights: {result['error']}"
        
        # Use the formatted report if available
        if 'formatted_report' in result:
            return result['formatted_report']
        
        # Otherwise build a basic report
        response = f"# Counterparty Intelligence Report: {result.get('counterparty_name', 'Unknown')}\n\n"
        
        if 'summary' in result:
            response += f"## Executive Summary\n\n{result['summary']}\n\n"
        
        if 'sources_summary' in result:
            response += "## Key Findings\n\n"
            for source_type, data in result['sources_summary'].items():
                response += f"### {source_type.title()}\n"
                response += f"- {data.get('count', 0)} sources found\n"
                if 'highlights' in data:
                    for highlight in data['highlights'][:3]:
                        response += f"- {highlight}\n"
                response += "\n"
        
        if 'total_sources' in result:
            response += f"\n---\n*Total sources analyzed: {result['total_sources']}*\n"
        
        return response
    
    def _format_generic_result(self, result: Any) -> str:
        """Format generic tool result"""
        if isinstance(result, dict):
            return json.dumps(result, indent=2, default=str)
        return str(result)
    
    def _generate_final_answer(self, state: AgentState) -> str:
        """Generate final answer when no tool was executed"""
        if state.get('observation'):
            return f"Based on the analysis:\n\n{state['observation']}"
        return "I couldn't process your request. Please try rephrasing or ask for help."
    
    def _get_tools_used(self, state: AgentState) -> List[str]:
        """Get list of tools used during execution"""
        tools = []
        if state.get('selected_tool'):
            tools.append(state['selected_tool'])
        return tools
    
    def _get_help_message(self) -> str:
        """Get help message with available capabilities"""
        return """# Available Capabilities

I can help you with:

## Risk Analysis
- Analyze counterparty credit risk and exposures
- Check limit breaches and utilization
- Example: "Analyze risk for Northbridge Capital" or "Check limits for AC001"

## Data Queries
- List available data tables
- Execute SQL queries on DuckDB
- Example: "List all tables" or "Query trades data"

## Information Search
- Search the web for information
- Look up topics on Wikipedia
- Example: "Search for counterparty risk management" or "Wikipedia Basel III"

Please specify what you'd like me to help you with!"""

