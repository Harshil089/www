from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient

def fetch_rules(query: str) -> str:
    """Fetch and search Wazuh rules based on natural language query"""
    try:
        wazuh = WazuhClient()
        rules = wazuh.get_rules()
        
        if rules.get('error', 0) != 0:
            return f"Error fetching rules: {rules['error']}"
        
        items = rules.get('data', {}).get('affected_items', [])
        
        if not items:
            return "No rules found."
        
        result = f"Found {len(items)} rules:\n\n"
        for i, rule in enumerate(items[:5], 1):
            result += f"{i}. Rule {rule.get('id', 'N/A')}: {rule.get('description', 'No description')}\n"
            result += f"   Level: {rule.get('level', 'N/A')} | Groups: {', '.join(rule.get('groups', []))}\n\n"
        
        if len(items) > 5:
            result += f"... and {len(items) - 5} more rules"
        
        return result
    except Exception as e:
        return f"Error processing rule query: {str(e)}"

@tool
def rule_tool(query: str) -> str:
    """Fetch and search Wazuh rules. Use for queries about rule definitions, rule IDs, or rule management."""
    return fetch_rules(query)