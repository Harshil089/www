from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient

def fetch_agents(query: str) -> str:
    """Fetch and analyze Wazuh agents status"""
    try:
        wazuh = WazuhClient()
        agents = wazuh.get_agents()
        
        if agents.get('error', 0) != 0:
            return f"Error fetching agents: {agents['error']}"
        
        items = agents.get('data', {}).get('affected_items', [])
        
        if not items:
            return "No agents found."
        
        active_count = sum(1 for agent in items if agent.get('status') == 'active')
        total_count = len(items)
        
        result = f"Agent Status Summary:\n"
        result += f"Total Agents: {total_count}\n"
        result += f"Active Agents: {active_count}\n"
        result += f"Inactive Agents: {total_count - active_count}\n\n"
        
        result += "Recent Agents:\n"
        for i, agent in enumerate(items[:5], 1):
            status = agent.get('status', 'unknown')
            result += f"{i}. {agent.get('name', 'N/A')} ({agent.get('id', 'N/A')})\n"
            result += f"   Status: {status} | OS: {agent.get('os', {}).get('name', 'N/A')}\n"
            result += f"   IP: {agent.get('ip', 'N/A')} | Last Keep Alive: {agent.get('lastKeepAlive', 'N/A')}\n\n"
        
        return result
    except Exception as e:
        return f"Error processing agent query: {str(e)}"

@tool
def agent_tool(query: str) -> str:
    """Fetch and analyze Wazuh agent status. Use for queries about agent health, connectivity, or agent management."""
    return fetch_agents(query)