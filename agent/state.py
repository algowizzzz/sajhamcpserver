"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Agent State Management
"""
from typing import TypedDict, List, Dict, Any, Annotated
import operator


class AgentState(TypedDict):
    """State for the agent workflow"""
    # User input
    query: str
    
    # Conversation history
    messages: Annotated[List[Dict[str, Any]], operator.add]
    
    # Tool execution
    selected_tool: str
    tool_input: Dict[str, Any]
    tool_output: Any
    
    # Agent reasoning
    thought: str
    observation: str
    
    # Control flow
    iteration: int
    max_iterations: int
    
    # Final response
    final_answer: str
    
    # Metadata
    agent_config: Dict[str, Any]

