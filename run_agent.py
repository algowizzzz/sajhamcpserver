#!/usr/bin/env python3
"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Simple CLI for running AI agents
"""
import argparse
import sys
import logging
from agent import AgentExecutor, AgentConfig

# Setup logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s - %(message)s'
)

def main():
    parser = argparse.ArgumentParser(
        description='AI Agent CLI - Execute queries using configured agents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s "Analyze risk for Northbridge Capital"
  %(prog)s --agent risk_analyst_agent "Check limits for AC001"
  %(prog)s --list-agents
  %(prog)s --interactive
        '''
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Query to execute'
    )
    
    parser.add_argument(
        '--agent', '-a',
        default='default_agent',
        help='Agent to use (default: default_agent)'
    )
    
    parser.add_argument(
        '--list-agents', '-l',
        action='store_true',
        help='List available agents'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Start interactive mode'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    
    config_manager = AgentConfig()
    
    # List agents
    if args.list_agents:
        print("\nAvailable Agents:")
        print("-" * 60)
        agents = config_manager.list_available_agents()
        for agent in agents:
            print(f"\n{agent['name']}")
            print(f"  Description: {agent['description']}")
            print(f"  Tools: {agent['tools_count']}")
        print()
        return 0
    
    # Interactive mode
    if args.interactive:
        return interactive_mode(config_manager, args.agent)
    
    # Execute single query
    if not args.query:
        parser.print_help()
        return 1
    
    # Load agent and execute
    print(f"\nLoading agent: {args.agent}...")
    config = config_manager.load_agent_config(args.agent)
    agent = AgentExecutor(config)
    
    print(f"Executing query: {args.query}\n")
    print("-" * 60)
    
    result = agent.run(args.query)
    
    print(result['final_answer'])
    print("\n" + "-" * 60)
    print(f"Iterations: {result['iterations']} | Tools: {', '.join(result['tools_used']) or 'None'}")
    print()
    
    return 0

def interactive_mode(config_manager, agent_name):
    """Run agent in interactive mode"""
    print("\n" + "=" * 60)
    print("  AI Agent - Interactive Mode")
    print("=" * 60)
    print(f"\nUsing agent: {agent_name}")
    print("Type 'help' for commands, 'quit' or 'exit' to leave\n")
    
    config = config_manager.load_agent_config(agent_name)
    agent = AgentExecutor(config)
    
    while True:
        try:
            query = input("\n🤖 > ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if query.lower() == 'help':
                print_help()
                continue
            
            if query.lower().startswith('switch '):
                new_agent = query.split(' ', 1)[1]
                try:
                    config = config_manager.load_agent_config(new_agent)
                    agent = AgentExecutor(config)
                    agent_name = new_agent
                    print(f"\n✓ Switched to agent: {agent_name}")
                except Exception as e:
                    print(f"\n✗ Error switching agent: {e}")
                continue
            
            # Execute query
            print("\nThinking...")
            result = agent.run(query)
            
            print("\n" + "-" * 60)
            print(result['final_answer'])
            print("-" * 60)
            print(f"📊 Stats: {result['iterations']} iterations | " 
                  f"Tools: {', '.join(result['tools_used']) or 'None'}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    return 0

def print_help():
    """Print interactive mode help"""
    print("""
Available Commands:
  help              - Show this help message
  switch <agent>    - Switch to a different agent
  quit, exit, q     - Exit interactive mode
  
Examples:
  Analyze risk for AC001
  List all tables
  Check limits for Northbridge Capital
    """)

if __name__ == "__main__":
    sys.exit(main())

